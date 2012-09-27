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
from datetime import datetime
import os
import subprocess
import sys
import time
import glob
import SlapOSControler

from ProcessManager import SubprocessError, ProcessManager, CancellationError
from Updater import Updater
from erp5.util import taskdistribution

DEFAULT_SLEEP_TIMEOUT = 120 # time in seconds to sleep
supervisord_pid_file = None

PROFILE_PATH_KEY = 'profile_path'


class DummyLogger(object):
  def __init__(self, func):
    for name in ('trace', 'debug', 'info', 'warn', 'warning', 'error',
      'critical', 'fatal'):
       setattr(self, name, func)


class TestNode(object):

  def __init__(self, log, config):
    self.log = log
    self.config = config
    self.process_manager = ProcessManager(log)
    self.process_manager.supervisord_pid_file = os.path.join(config['instance_root'], 'var', 'run',
          'supervisord.pid')

  def run(self):
    log = self.log
    process_manager = self.process_manager
    config = self.config
    slapgrid = None
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

    retry = False
    retry_software_count = 0
    same_revision_count = 0
    try:
      while True:
        try:
          # kill processes from previous loop if any
          process_manager.killPreviousRun()
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
              log=log, process_manager=process_manager)
            updater.checkout()
            revision = "-".join(updater.getRevision())
            full_revision_list.append('%s=%s' % (repository_id, revision))
          revision = ','.join(full_revision_list)
          if previous_revision == revision:
            log('Same Revision')
            same_revision_count += 1
            if not(retry) and same_revision_count <= 2:
              log('Sleeping a bit since same revision')
              time.sleep(DEFAULT_SLEEP_TIMEOUT)
              continue
            same_revision_count = 0
            log('Retrying install or checking if previous test was cancelled')
          retry = False
          previous_revision = revision
          portal_url = config['test_suite_master_url']
          portal = taskdistribution.TaskDistributionTool(portal_url, logger = DummyLogger(log))
          test_result = portal.createTestResult(revision,[],config['test_node_title'],False,test_suite_title,config['project_title'])
          remote_test_result_needs_cleanup = True
          log("testnode, test_result : %r" % (test_result, ))
          if test_result is not None:
            if config.get('log_file'):
              log_file_name = config['log_file']
              log_file = open(log_file_name)
              log_file.seek(0,2)
              log_file.seek(-min(5000,log_file.tell()),2)
              test_result.addWatch(log_file_name,log_file,max_history_bytes=10000)
            if revision != test_result.revision:
              previous_revision = test_result.revision
              log('Disagreement on tested revision, checking out:')
              for i, repository_revision in enumerate(previous_revision.split(',')):
                vcs_repository = vcs_repository_list[i]
                repository_path = vcs_repository['repository_path']
                revision = repository_revision.rsplit('-', 1)[1]
                # other testnodes on other boxes are already ready to test another
                # revision
                log('  %s at %s' % (repository_path, revision))
                updater = Updater(repository_path, git_binary=config['git_binary'],
                                  revision=revision, log=log,
                                  process_manager=process_manager)
                updater.checkout()

            # Now prepare the installation of SlapOS and create instance
            slapproxy_log = os.path.join(config['log_directory'],
                'slapproxy.log')
            log('Configured slapproxy log to %r' % slapproxy_log)
            log('testnode, retry_software_count : %r' % retry_software_count)
            slapos_controler = SlapOSControler.SlapOSControler(config,
              log=log, slapproxy_log=slapproxy_log, process_manager=process_manager,
              reset_software=(retry_software_count>0 and retry_software_count%10 == 0))
            for method_name in ("runSoftwareRelease", "runComputerPartition",):
              slapos_method = getattr(slapos_controler, method_name)
              status_dict = slapos_method(config,
                environment=config['environment'],
                )
              if status_dict['status_code'] != 0:
                retry = True
                retry_software_count += 1
                raise SubprocessError(status_dict)
              else:
                retry_software_count = 0
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
            # result. We only do cleanup if the test runner itself is not able
            # to run.
            process_manager.spawn(*invocation_list,
              cwd=config['test_suite_directory'],
              log_prefix='runTestSuite', get_output=False)
            if test_result is not None:
              test_result.removeWatch(log_file_name)
        except SubprocessError, e:
          log("SubprocessError", exc_info=sys.exc_info())
          if test_result is not None:
            test_result.removeWatch(log_file_name)
          if remote_test_result_needs_cleanup:
            status_dict = e.status_dict or {}
            test_result.reportFailure(
              command = status_dict.get('command'),
              stdout = status_dict.get('stdout'),
              stderr = status_dict.get('stderr'),
            )
          log("SubprocessError, going to sleep %s" % DEFAULT_SLEEP_TIMEOUT)
          time.sleep(DEFAULT_SLEEP_TIMEOUT)
          continue
        except CancellationError, e:
          log("CancellationError", exc_info=sys.exc_info())
          process_manager.under_cancellation = False
          retry = True
          continue
        except:
          log("erp5testnode exception", exc_info=sys.exc_info())
          raise
    finally:
      # Nice way to kill *everything* generated by run process -- process
      # groups working only in POSIX compilant systems
      # Exceptions are swallowed during cleanup phase
      log('Testnode.run, finally close')
      process_manager.killPreviousRun()
      if test_result is not None:
        try:
          test_result.removeWatch(log_file_name)
        except KeyError:
           log("KeyError, Watcher already deleted or not added correctly")
