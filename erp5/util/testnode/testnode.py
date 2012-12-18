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
from datetime import datetime,timedelta
import os
import subprocess
import sys
import time
import glob
import SlapOSControler
import json
import time
import shutil
from ProcessManager import SubprocessError, ProcessManager, CancellationError
from subprocess import CalledProcessError
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

class SlapOSInstance(object):

  def __init__(self):
    self.retry_software_count = 0
    self.retry = False

  def edit(self, **kw):
    self.__dict__.update(**kw)
    self._checkData()

  def _checkData(self):
    pass

def deunicodeData(data):
  if isinstance(data, list):
    new_data = []
    for sub_data in data:
      new_data.append(deunicodeData(sub_data))
  elif isinstance(data, unicode):
    new_data = data.encode('utf8')
  elif isinstance(data, dict):
    new_data = {}
    for key, value in data.iteritems():
      key = deunicodeData(key)
      value = deunicodeData(value)
      new_data[key] = value
  return new_data

class NodeTestSuite(SlapOSInstance):

  def __init__(self, reference):
    super(NodeTestSuite, self).__init__()
    self.reference = reference

  def edit(self, **kw):
    super(NodeTestSuite, self).edit(**kw)

  def _checkData(self):
    if getattr(self, "working_directory", None) is not None:
      if not(self.working_directory.endswith(os.path.sep + self.reference)):
        self.working_directory = os.path.join(self.working_directory,
                                             self.reference)
      SlapOSControler.createFolder(self.working_directory)
      self.test_suite_directory = os.path.join(
                                   self.working_directory, "test_suite")
      self.custom_profile_path = os.path.join(self.working_directory,
                                 'software.cfg')
    if getattr(self, "vcs_repository_list", None) is not None:
      for vcs_repository in self.vcs_repository_list:
        buildout_section_id = vcs_repository.get('buildout_section_id', None)
        repository_id = buildout_section_id or \
                        vcs_repository.get('url').split('/')[-1].split('.')[0]
        repository_path = os.path.join(self.working_directory,repository_id)
        vcs_repository['repository_id'] = repository_id
        vcs_repository['repository_path'] = repository_path

class TestNode(object):

  def __init__(self, log, config):
    self.log = log
    self.config = config or {}
    self.process_manager = ProcessManager(log)
    self.node_test_suite_dict = {}
    # hack until slapos.cookbook is updated
    if self.config.get('working_directory', '').endswith("slapos/"):
      self.config['working_directory'] = self.config[
        'working_directory'][:-(len("slapos/"))] + "testnode"

  def checkOldTestSuite(self,test_suite_data):
    config = self.config
    installed_reference_set = set(os.listdir(config['working_directory']))
    wished_reference_set = set([x['test_suite_reference'] for x in test_suite_data])
    to_remove_reference_set = installed_reference_set.difference(
                                 wished_reference_set)
    for y in to_remove_reference_set:
      fpath = os.path.join(config['working_directory'],y)
      self.delNodeTestSuite(y)
      if os.path.isdir(fpath):
       shutil.rmtree(fpath)
      else:
       os.remove(fpath)

  def getNodeTestSuite(self, reference):
    node_test_suite = self.node_test_suite_dict.get(reference)
    if node_test_suite is None:
      node_test_suite = NodeTestSuite(reference)
      self.node_test_suite_dict[reference] = node_test_suite
    return node_test_suite

  def delNodeTestSuite(self, reference):
    if self.node_test_suite_dict.has_key(reference):
      self.node_test_suite_dict.pop(reference)

  def constructProfile(self, node_test_suite):
    config = self.config
    profile_content = ''
    assert len(node_test_suite.vcs_repository_list), "we must have at least one repository"
    profile_path_count = 0
    profile_content_list = []
    for vcs_repository in node_test_suite.vcs_repository_list:
      url = vcs_repository['url']
      buildout_section_id = vcs_repository.get('buildout_section_id', None)
      repository_path = vcs_repository['repository_path']
      try:
        profile_path = vcs_repository[PROFILE_PATH_KEY]
      except KeyError:
        pass
      else:
        profile_path_count += 1
        if profile_path_count > 1:
          raise ValueError(PROFILE_PATH_KEY + ' defined more than once')
        profile_content_list.append("""
[buildout]
extends = %(software_config_path)s
""" %  {'software_config_path': os.path.join(repository_path, profile_path)})

      if not(buildout_section_id is None):
        profile_content_list.append("""
[%(buildout_section_id)s]
repository = %(repository_path)s
branch = %(branch)s
""" %  {'buildout_section_id': buildout_section_id,
   'repository_path' : repository_path,
   'branch' : vcs_repository.get('branch','master')})
    if not profile_path_count:
      raise ValueError(PROFILE_PATH_KEY + ' not defined')
    custom_profile = open(node_test_suite.custom_profile_path, 'w')
    # sort to have buildout section first
    profile_content_list.sort(key=lambda x: [x, ''][x.startswith('\n[buildout]')])
    custom_profile.write(''.join(profile_content_list))
    custom_profile.close()
    sys.path.append(repository_path)

  def getAndUpdateFullRevisionList(self, node_test_suite):
    full_revision_list = []
    config = self.config
    log = self.log
    for vcs_repository in node_test_suite.vcs_repository_list:
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
         log=log, process_manager=self.process_manager)
      updater.checkout()
      revision = "-".join(updater.getRevision())
      full_revision_list.append('%s=%s' % (repository_id, revision))
    node_test_suite.revision = ','.join(full_revision_list)
    return full_revision_list

  def addWatcher(self,test_result):
    config = self.config
    if config.get('log_file'):
     log_file_name = config['log_file']
     log_file = open(log_file_name)
     log_file.seek(0, 2)
     log_file.seek(-min(5000, log_file.tell()), 2)
     test_result.addWatch(log_file_name,log_file,max_history_bytes=10000)
     return log_file_name

  def checkRevision(self, test_result, node_test_suite):
    config = self.config
    log = self.log
    if node_test_suite.revision != test_result.revision:
     log('Disagreement on tested revision, checking out: %r' % (
          (node_test_suite.revision,test_result.revision),))
     for i, repository_revision in enumerate(test_result.revision.split(',')):
      vcs_repository = node_test_suite.vcs_repository_list[i]
      repository_path = vcs_repository['repository_path']
      revision = repository_revision.rsplit('-', 1)[1]
      # other testnodes on other boxes are already ready to test another
      # revision
      log('  %s at %s' % (repository_path, node_test_suite.revision))
      updater = Updater(repository_path, git_binary=config['git_binary'],
                        revision=revision, log=log,
                        process_manager=self.process_manager)
      updater.checkout()
      node_test_suite.revision = test_result.revision

  def _prepareSlapOS(self, working_directory, slapos_instance,
          create_partition=1, software_path_list=None, **kw):
    """
    Launch slapos to build software and partitions
    """
    slapproxy_log = os.path.join(self.config['log_directory'],
                                  'slapproxy.log')
    self.log('Configured slapproxy log to %r' % slapproxy_log)
    reset_software = slapos_instance.retry_software_count > 10
    self.log('testnode, retry_software_count : %r' % \
             slapos_instance.retry_software_count)
    self.slapos_controler = SlapOSControler.SlapOSControler(
      working_directory, self.config, self.log)
    self.slapos_controler.initializeSlapOSControler(slapproxy_log=slapproxy_log,
       process_manager=self.process_manager, reset_software=reset_software,
       software_path_list=software_path_list)
    self.process_manager.supervisord_pid_file = os.path.join(\
         self.slapos_controler.instance_root, 'var', 'run', 'supervisord.pid')
    method_list= ["runSoftwareRelease"]
    if create_partition:
      method_list.append("runComputerPartition")
    for method_name in method_list:
      slapos_method = getattr(self.slapos_controler, method_name)
      status_dict = slapos_method(self.config,
                                  environment=self.config['environment'],
                                 )
      if status_dict['status_code'] != 0:
         slapos_instance.retry = True
         slapos_instance.retry_software_count += 1
         raise SubprocessError(status_dict)
      else:
         slapos_instance.retry_software_count = 0
    return status_dict

  def prepareSlapOSForTestNode(self, test_node_slapos):
    """
    We will build slapos software needed by the testnode itself,
    like the building of selenium-runner by default
    """
    return self._prepareSlapOS(self.config['slapos_directory'],
              test_node_slapos, create_partition=0,
              software_path_list=self.config.get("software_list"))

  def prepareSlapOSForTestSuite(self, node_test_suite):
    return self._prepareSlapOS(node_test_suite.working_directory,
              node_test_suite,
              software_path_list=[node_test_suite.custom_profile_path])

  def _dealShebang(self,run_test_suite_path):
    line = open(run_test_suite_path, 'r').readline()
    invocation_list = []
    if line[:2] == '#!':
      invocation_list = line[2:].split()
    return invocation_list

  def runTestSuite(self, node_test_suite, portal_url):
    config = self.config
    parameter_list = []
    run_test_suite_path_list = glob.glob("%s/*/bin/runTestSuite" % \
        self.slapos_controler.instance_root)
    if not len(run_test_suite_path_list):
      raise ValueError('No runTestSuite provided in installed partitions.')
    run_test_suite_path = run_test_suite_path_list[0]
    run_test_suite_revision = node_test_suite.revision
    # Deal with Shebang size limitation
    invocation_list = self._dealShebang(run_test_suite_path)
    invocation_list.extend([run_test_suite_path,
                           '--test_suite', node_test_suite.test_suite,
                           '--revision', node_test_suite.revision,
                           '--test_suite_title', node_test_suite.test_suite_title,
                           '--node_quantity', config['node_quantity'],
                           '--master_url', portal_url])
    firefox_bin_list = glob.glob("%s/soft/*/parts/firefox/firefox-slapos" % \
        config["slapos_directory"])
    if len(firefox_bin_list):
      parameter_list.append('--firefox_bin')
    xvfb_bin_list = glob.glob("%s/soft/*/parts/xserver/bin/Xvfb" % \
        config["slapos_directory"])
    if len(xvfb_bin_list):
      parameter_list.append('--xvfb_bin')
    supported_paramater_set = self.process_manager.getSupportedParameterSet(
                           run_test_suite_path, parameter_list)
    if '--firefox_bin' in supported_paramater_set:
      invocation_list.extend(["--firefox_bin", firefox_bin_list[0]])
    if '--xvfb_bin' in supported_paramater_set:
      invocation_list.extend(["--xvfb_bin", xvfb_bin_list[0]])
    bt5_path_list = config.get("bt5_path")
    if bt5_path_list not in ('', None,):
      invocation_list.extend(["--bt5_path", bt5_path_list])
    # From this point, test runner becomes responsible for updating test
    # result. We only do cleanup if the test runner itself is not able
    # to run.
    SlapOSControler.createFolder(node_test_suite.test_suite_directory,
                                 clean=True)
    self.process_manager.spawn(*invocation_list,
                          cwd=node_test_suite.test_suite_directory,
                          log_prefix='runTestSuite', get_output=False)

  def cleanUp(self,test_result):
    log = self.log
    log('Testnode.cleanUp')
    self.process_manager.killPreviousRun()
    if test_result is not None:
      try:
        test_result.removeWatch(self.config['log_file'])
      except KeyError:
        log("KeyError, Watcher already deleted or not added correctly")

  def run(self):
    log = self.log
    config = self.config
    slapgrid = None
    previous_revision_dict = {}
    revision_dict = {}
    test_result = None
    test_node_slapos = SlapOSInstance()
    test_node_slapos.edit(working_directory=self.config['slapos_directory'])
    try:
      while True:
        try:
          self.cleanUp(None)
          remote_test_result_needs_cleanup = False
          begin = time.time()
          self.prepareSlapOSForTestNode(test_node_slapos)
          portal_url = config['test_suite_master_url']
          portal = taskdistribution.TaskDistributionTool(portal_url, logger=DummyLogger(log))
          test_suite_portal = taskdistribution.TaskDistributor(portal_url, logger=DummyLogger(log))
          test_suite_json =  test_suite_portal.startTestSuite(config['test_node_title'])
          test_suite_data = deunicodeData(json.loads(test_suite_json))
          log("Got following test suite data from master : %r" % \
              (test_suite_data,))
          #Clean-up test suites
          self.checkOldTestSuite(test_suite_data)
          for test_suite in test_suite_data:
            remote_test_result_needs_cleanup = False
            node_test_suite = self.getNodeTestSuite(
               test_suite["test_suite_reference"])
            node_test_suite.edit(
               working_directory=self.config['working_directory'])
            node_test_suite.edit(**test_suite)
            run_software = True
            # Write our own software.cfg to use the local repository
            self.constructProfile(node_test_suite)
            # kill processes from previous loop if any
            self.process_manager.killPreviousRun()
            self.getAndUpdateFullRevisionList(node_test_suite)
            # Make sure we have local repository
            test_result = portal.createTestResult(node_test_suite.revision, [],
                     config['test_node_title'], False,
                     node_test_suite.test_suite_title,
                     node_test_suite.project_title)
            remote_test_result_needs_cleanup = True
            log("testnode, test_result : %r" % (test_result, ))
            if test_result is not None:
              log_file_name = self.addWatcher(test_result)
              self.checkRevision(test_result,node_test_suite)
              # Now prepare the installation of SlapOS and create instance
              status_dict = self.prepareSlapOSForTestSuite(node_test_suite)
              # Give some time so computer partitions may start
              # as partitions can be of any kind we have and likely will never have
              # a reliable way to check if they are up or not ...
              time.sleep(20)
              self.runTestSuite(node_test_suite,portal_url)
              test_result.removeWatch(log_file_name)
              # break the loop to get latest priorities from master
              break
            self.cleanUp(test_result)
        except (SubprocessError, CalledProcessError) as e:
          log("SubprocessError", exc_info=sys.exc_info())
          if test_result is not None:
            test_result.removeWatch(log_file_name)
          if remote_test_result_needs_cleanup:
            status_dict = e.status_dict or {}
            test_result.reportFailure(
              command=status_dict.get('command'),
              stdout=status_dict.get('stdout'),
              stderr=status_dict.get('stderr'),
            )
          continue
        except ValueError as e:
          # This could at least happens if runTestSuite is not found
          log("ValueError", exc_info=sys.exc_info())
          node_test_suite.retry_software_count += 1
        except CancellationError, e:
          log("CancellationError", exc_info=sys.exc_info())
          self.process_manager.under_cancellation = False
          node_test_suite.retry = True
          continue
        except:
            log("erp5testnode exception", exc_info=sys.exc_info())
            raise
        now = time.time()
        self.cleanUp(test_result)
        if (now-begin) < 120:
          sleep_time = 120 - (now-begin)
          log("End of processing, going to sleep %s" % sleep_time)
          time.sleep(sleep_time)
    finally:
      # Nice way to kill *everything* generated by run process -- process
      # groups working only in POSIX compilant systems
      # Exceptions are swallowed during cleanup phas
      log("GENERAL EXCEPTION, QUITING")
      self.cleanUp(test_result)
