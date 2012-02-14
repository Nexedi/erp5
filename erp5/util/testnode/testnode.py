##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################
import os
import pprint
import signal
import socket
import subprocess
import sys
import time
import xmlrpclib
import glob
import SlapOSControler
import logging

DEFAULT_SLEEP_TIMEOUT = 120 # time in seconds to sleep

class SubprocessError(EnvironmentError):
  def __init__(self, status_dict):
    self.status_dict = status_dict
  def __getattr__(self, name):
    return self.status_dict[name]
  def __str__(self):
    return 'Error %i' % self.status_code

from Updater import Updater

supervisord_pid_file = None
process_group_pid_set = set()
def sigterm_handler(signal, frame):
  for pgpid in process_group_pid_set:
    try:
      os.killpg(pgpid, signal.SIGTERM)
    except:
      pass
  sys.exit(1)

signal.signal(signal.SIGTERM, sigterm_handler)

def safeRpcCall(function, *args):
  # XXX: this method will try infinitive calls to backend
  # this can cause testnode to looked "stalled"
  retry = 64
  while True:
    try:
      return function(*args)
    except (socket.error, xmlrpclib.ProtocolError), e:
      logging.warning(e)
      pprint.pprint(args, file(function._Method__name, 'w'))
      time.sleep(retry)
      retry += retry >> 1

def getInputOutputFileList(config, command_name):
  stdout = open(os.path.join(
                config['log_directory'],'%s_out' % command_name),
                'w+')
  stdout.write("%s\n" % command_name)
  stderr = open(os.path.join(
                config['log_directory'],'%s_err' % command_name),
                'w+')
  return (stdout, stderr)

slapos_controler = None

def killPreviousRun():
  for pgpid in process_group_pid_set:
    try:
      os.killpg(pgpid, signal.SIGTERM)
    except:
      pass
  try:
    if os.path.exists(supervisord_pid_file):
      os.kill(int(open(supervisord_pid_file).read().strip()), signal.SIGTERM)
  except:
    pass

PROFILE_PATH_KEY = 'profile_path'

def run(config):
  log = config['logger']
  slapgrid = None
  global supervisord_pid_file
  supervisord_pid_file = os.path.join(config['instance_root'], 'var', 'run',
        'supervisord.pid')
  previous_revision = None

  run_software = True
  # Write our own software.cfg to use the local repository
  custom_profile_path = os.path.join(config['working_directory'], 'software.cfg')
  config['custom_profile_path'] = custom_profile_path
  vcs_repository_list = config['vcs_repository_list']
  profile_content = ''
  assert len(vcs_repository_list), "we must have at least one repository"
  try:
    # BBB: Accept global profile_path, which is the same as setting it for the
    # first configured repository.
    profile_path = config.pop(PROFILE_PATH_KEY)
  except KeyError:
    pass
  else:
    vcs_repository_list[0][PROFILE_PATH_KEY] = profile_path
  profile_path_count = 0
  for vcs_repository in vcs_repository_list:
    url = vcs_repository['url']
    buildout_section_id = vcs_repository.get('buildout_section_id', None)
    repository_id = buildout_section_id or \
                                  url.split('/')[-1].split('.')[0]
    repository_path = os.path.join(config['working_directory'],repository_id)
    vcs_repository['repository_id'] = repository_id
    vcs_repository['repository_path'] = repository_path
    try:
      profile_path = vcs_repository[PROFILE_PATH_KEY]
    except KeyError:
      pass
    else:
      profile_path_count += 1
      if profile_path_count > 1:
        raise ValueError(PROFILE_PATH_KEY + ' defined more than once')
      profile_content = """
[buildout]
extends = %(software_config_path)s
""" %  {'software_config_path': os.path.join(repository_path, profile_path)}

    if not(buildout_section_id is None):
      profile_content += """
[%(buildout_section_id)s]
repository = %(repository_path)s
branch = %(branch)s
""" %  {'buildout_section_id': buildout_section_id,
        'repository_path' : repository_path,
        'branch' : vcs_repository.get('branch','master')}

  if not profile_path_count:
    raise ValueError(PROFILE_PATH_KEY + ' not defined')
  custom_profile = open(custom_profile_path, 'w')
  custom_profile.write(profile_content)
  custom_profile.close()
  config['repository_path'] = repository_path
  sys.path.append(repository_path)
  test_suite_title = config['test_suite_title'] or config['test_suite']

  retry_software = False
  try:
    while True:
      remote_test_result_needs_cleanup = False
      # kill processes from previous loop if any
      try:
        killPreviousRun()
        process_group_pid_set.clear()
        full_revision_list = []
        # Make sure we have local repository
        for vcs_repository in vcs_repository_list:
          repository_path = vcs_repository['repository_path']
          repository_id = vcs_repository['repository_id']
          if not os.path.exists(repository_path):
            parameter_list = [config['git_binary'], 'clone',
                              vcs_repository['url']]
            if vcs_repository.get('branch') is not None:
              parameter_list.extend(['-b',vcs_repository.get('branch')])
            parameter_list.append(repository_path)
            log(subprocess.check_output(parameter_list, stderr=subprocess.STDOUT))
          # Make sure we have local repository
          updater = Updater(repository_path, git_binary=config['git_binary'],
            log=log, realtime_output=False)
          updater.checkout()
          revision = "-".join(updater.getRevision())
          full_revision_list.append('%s=%s' % (repository_id, revision))
        revision = ','.join(full_revision_list)
        if previous_revision == revision:
          log('Sleeping a bit')
          time.sleep(DEFAULT_SLEEP_TIMEOUT)
          if not(retry_software):
            continue
          log('Retrying install')
        retry_software = False
        previous_revision = revision

        portal_url = config['test_suite_master_url']
        test_result_path = None
        test_result = (test_result_path, revision)
        if portal_url:
          if portal_url[-1] != '/':
            portal_url += '/'
          portal = xmlrpclib.ServerProxy("%s%s" %
                      (portal_url, 'portal_task_distribution'),
                      allow_none=1)
          master = portal
          assert safeRpcCall(master.getProtocolRevision) == 1
          test_result = safeRpcCall(master.createTestResult,
            config['test_suite'], revision, [],
            False, test_suite_title,
            config['test_node_title'], config['project_title'])
          remote_test_result_needs_cleanup = True
        log("testnode, test_result : %r" % (test_result, ))
        if test_result:
          test_result_path, test_revision = test_result
          if revision != test_revision:
            log('Disagreement on tested revision, checking out:')
            for i, repository_revision in enumerate(test_revision.split(',')):
              vcs_repository = vcs_repository_list[i]
              repository_path = vcs_repository['repository_path']
              revision = repository_revision.rsplit('-', 1)[1]
              # other testnodes on other boxes are already ready to test another
              # revision
              log('  %s at %s' % (repository_path, revision))
              updater = Updater(repository_path, git_binary=config['git_binary'],
                                revision=revision, log=log,
                                realtime_output=False)
              updater.checkout()

          # Now prepare the installation of SlapOS and create instance
          slapproxy_log = os.path.join(config['log_directory'],
              'slapproxy.log')
          log('Configured slapproxy log to %r' % slapproxy_log)
          slapos_controler = SlapOSControler.SlapOSControler(config,
            process_group_pid_set=process_group_pid_set, log=log,
            slapproxy_log=slapproxy_log)
          for method_name in ("runSoftwareRelease", "runComputerPartition",):
            stdout, stderr = getInputOutputFileList(config, method_name)
            slapos_method = getattr(slapos_controler, method_name)
            status_dict = slapos_method(config,
              environment=config['environment'],
              process_group_pid_set=process_group_pid_set,
              stdout=stdout, stderr=stderr
              )
            if status_dict['status_code'] != 0:
              retry_software = True
              raise SubprocessError(status_dict)
          # Give some time so computer partitions may start
          # as partitions can be of any kind we have and likely will never have
          # a reliable way to check if they are up or not ...
          time.sleep(20)

          run_test_suite_path_list = glob.glob("%s/*/bin/runTestSuite" %config['instance_root'])
          if not len(run_test_suite_path_list):
            raise ValueError('No runTestSuite provided in installed partitions.')
          run_test_suite_path = run_test_suite_path_list[0]
          run_test_suite_revision = revision
          if isinstance(revision, tuple):
            revision = ','.join(revision)
          # Deal with Shebang size limitation
          line = open(run_test_suite_path, 'r').readline()
          invocation_list = []
          if line[:2] == '#!':
            invocation_list = line[2:].split()
          invocation_list.extend([run_test_suite_path,
                                  '--test_suite', config['test_suite'],
                                  '--revision', revision,
                                  '--test_suite_title', test_suite_title,
                                  '--node_quantity', config['node_quantity'],
                                  '--master_url', portal_url])
          bt5_path_list = config.get("bt5_path")
          if bt5_path_list not in ('', None,):
            invocation_list.extend(["--bt5_path", bt5_path_list])
          # From this point, test runner becomes responsible for updating test
          # result.
          # XXX: is it good for all cases (eg: test runner fails too early for
          # any custom code to pick the failure up and react ?)
          remote_test_result_needs_cleanup = False
          log("call process : %r", (invocation_list,))
          run_test_suite = subprocess.Popen(invocation_list,
            preexec_fn=os.setsid, cwd=config['test_suite_directory'],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
          process_group_pid_set.add(run_test_suite.pid)
          log(run_test_suite.communicate()[0])
          process_group_pid_set.remove(run_test_suite.pid)
      except SubprocessError, e:
        if remote_test_result_needs_cleanup:
          safeRpcCall(master.reportTaskFailure,
            test_result_path, e.status_dict, config['test_node_title'])
        time.sleep(DEFAULT_SLEEP_TIMEOUT)
        continue

  finally:
    # Nice way to kill *everything* generated by run process -- process
    # groups working only in POSIX compilant systems
    # Exceptions are swallowed during cleanup phase
    killPreviousRun()
