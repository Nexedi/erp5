from unittest import TestCase

from erp5.util.testnode.testnode import TestNode
from erp5.util.testnode.testnode import SlapOSInstance
from erp5.util.testnode.ProcessManager import ProcessManager, SubprocessError

from erp5.util.testnode.SlapOSControler import SlapOSControler
from erp5.util.testnode.SlapOSControler import createFolder
from erp5.util.taskdistribution import TaskDistributor
from erp5.util.taskdistribution import TaskDistributionTool
from erp5.util.taskdistribution import TestResultProxy
import os
import shutil
import subprocess
import tempfile
import json
import time
import types
import re

class ERP5TestNode(TestCase):

  def setUp(self):
    self._temp_dir = tempfile.mkdtemp()
    self.working_directory = os.path.join(self._temp_dir, 'testnode')
    self.slapos_directory = os.path.join(self._temp_dir, 'slapos')
    self.test_suite_directory = os.path.join(self._temp_dir,'test_suite')
    self.environment = os.path.join(self._temp_dir,'environment')
    self.log_directory = os.path.join(self._temp_dir,'var/log/testnode')
    self.log_file = os.path.join(self.log_directory,'test.log')
    self.remote_repository0 = os.path.join(self._temp_dir, 'rep0')
    self.remote_repository1 = os.path.join(self._temp_dir, 'rep1')
    self.remote_repository2 = os.path.join(self._temp_dir, 'rep2')
    self.system_temp_folder = os.path.join(self._temp_dir,'tmp')
    os.mkdir(self.working_directory)
    os.mkdir(self.slapos_directory)
    os.mkdir(self.test_suite_directory)
    os.mkdir(self.environment)
    os.mkdir(self.system_temp_folder)
    os.makedirs(self.log_directory)
    os.close(os.open(self.log_file,os.O_CREAT))
    os.mkdir(self.remote_repository0)
    os.mkdir(self.remote_repository1)
    os.mkdir(self.remote_repository2)
    def log(*args,**kw):
      for arg in args:
        print "TESTNODE LOG : %r" % (arg,)
    self.log = log

  def tearDown(self):
    shutil.rmtree(self._temp_dir, True)

  def getTestNode(self):
    # XXX how to get property the git path ?
    config = {}
    config["git_binary"] = "git"
    config["slapos_directory"] = config["working_directory"] = self.working_directory
    config["node_quantity"] = 3
    config["test_suite_directory"] = self.test_suite_directory
    config["environment"] = self.environment
    config["log_directory"] = self.log_directory
    config["log_file"] = self.log_file
    config["test_suite_master_url"] = None
    config["test_node_title"] = "Foo-Test-Node"
    config["system_temp_folder"] = self.system_temp_folder
    return TestNode(self.log, config)

  def getTestSuiteData(self, add_third_repository=False, reference="foo"):
    data = [{
       "test_suite": "Foo",
       "project_title": reference,
       "test_suite_title": "Foo-Test",
       "test_suite_reference": reference,
       "vcs_repository_list": [
            {'url': self.remote_repository0,
             'profile_path': 'software.cfg',
             'branch': 'master'},
            {'url': self.remote_repository1,
             'buildout_section_id': 'rep1',
             'branch': 'master'}]}]
    if add_third_repository:
      # add a third repository
      # insert in position zero since we already had bug when the profile_path
      # was defined in non-zero position when generating the profile
      data[0]['vcs_repository_list'].insert(0,
            {'url': self.remote_repository2,
             'buildout_section_id': 'rep2',
             'branch': 'foo'})
    return data

  def updateNodeTestSuiteData(self, node_test_suite,
                              add_third_repository=False):
    node_test_suite.edit(working_directory=self.working_directory,
       **self.getTestSuiteData(add_third_repository=add_third_repository)[0])

  def getCaller(self, **kw):
    class Caller(object):

      def __init__(self, **kw):
        self.__dict__.update(**kw)

      def __call__(self, command):
        return subprocess.check_output(command, **self.__dict__)
    return Caller(**kw)

  def generateTestRepositoryList(self, add_third_repository=False):
    commit_dict = {}
    repository_list = [self.remote_repository0, self.remote_repository1]
    if add_third_repository:
      repository_list.append(self.remote_repository2)
    for i, repository_path in enumerate(repository_list):
      call = self.getCaller(cwd=repository_path)
      call("git init".split())
      git_config = open(os.path.join(repository_path, '.git', 'config'), 'a')
      git_config.write("""
[user]
  name = a b
  email = a@b.c
""")
      git_config.close()
      call("touch first_file".split())
      call("git add first_file".split())
      call("git commit -v -m first_commit".split())
      my_file = open(os.path.join(repository_path, 'first_file'), 'w')
      my_file.write("initial_content%i" % i)
      my_file.close()
      call("git commit -av -m next_commit".split())
      output = call(['git', 'log', '--format=%H %s'])
      output = output.strip()
      output_line_list = output.split("\n")
      self.assertEquals(2, len(output_line_list))
      expected_commit_subject_list = ["next_commit", "first_commit"]
      commit_subject_list = [x.split()[1] for x in output_line_list]
      self.assertEquals(expected_commit_subject_list, commit_subject_list)
      commit_dict['rep%i' % i] = [x.split() for x in output_line_list]
      if repository_path == self.remote_repository2:
        output = call('git checkout master -b foo'.split())
    # commit_dict looks like
    # {'rep1': [['6669613db7239c0b7f6e1fdb82af6f583dcb3a94', 'next_commit'],
    #           ['4f1d14de1b04b4f878a442ee859791fa337bcf85', 'first_commit']],
    #  'rep0': [['fb2a61882148d705fd10ecd87278b458a59920a9', 'next_commit'],
    #           ['4f1d14de1b04b4f878a442ee859791fa337bcf85', 'first_commit']]}
    return commit_dict

  def test_01_getDelNodeTestSuite(self):
    """
    We should be able to get/delete NodeTestSuite objects inside test_node
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.assertEquals(0, node_test_suite.retry_software_count)
    node_test_suite.retry_software_count = 2
    self.assertEquals(2, node_test_suite.retry_software_count)
    node_test_suite = test_node.delNodeTestSuite('foo')
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.assertEquals(0, node_test_suite.retry_software_count)

  def test_02_NodeTestSuiteWorkingDirectory(self):
    """
    Make sure we extend the working path with the node_test_suite reference
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    node_test_suite.edit(working_directory=self.working_directory)
    self.assertEquals("%s/foo" % self.working_directory,
                      node_test_suite.working_directory)
    self.assertEquals("%s/foo/test_suite" % self.working_directory,
                      node_test_suite.test_suite_directory)

  def test_03_NodeTestSuiteCheckDataAfterEdit(self):
    """
    When a NodeTestSuite instance is edited, the method _checkData
    analyse properties and add new ones
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    self.assertEquals(2, len(node_test_suite.vcs_repository_list))
    repository_path_list = []
    for vcs_repository in node_test_suite.vcs_repository_list:
      repository_path_list.append(vcs_repository['repository_path'])
    expected_list = ["%s/rep0" % node_test_suite.working_directory,
                     "%s/rep1" % node_test_suite.working_directory]
    self.assertEquals(expected_list, repository_path_list)

  def test_04_constructProfile(self):
    """
    Check if the software profile is correctly generated
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite, add_third_repository=True)
    test_node.constructProfile(node_test_suite)
    self.assertEquals("%s/software.cfg" % (node_test_suite.working_directory,),
                      node_test_suite.custom_profile_path)
    profile = open(node_test_suite.custom_profile_path, 'r')
    expected_profile = """
[buildout]
extends = %(temp_dir)s/testnode/foo/rep0/software.cfg

[rep1]
repository = %(temp_dir)s/testnode/foo/rep1
branch = master

[rep2]
repository = %(temp_dir)s/testnode/foo/rep2
branch = foo
""" % {'temp_dir': self._temp_dir}
    self.assertEquals(expected_profile, profile.read())
    profile.close()

  def test_05_getAndUpdateFullRevisionList(self):
    """
    Check if we clone correctly repositories and get right revisions
    """
    commit_dict = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    self.assertEquals(2, len(rev_list))
    self.assertEquals(rev_list[0], 'rep0=2-%s' % commit_dict['rep0'][0][0])
    self.assertEquals(rev_list[1], 'rep1=2-%s' % commit_dict['rep1'][0][0])
    my_file = open(os.path.join(self.remote_repository1, 'first_file'), 'w')
    my_file.write("next_content")
    my_file.close()
    call = self.getCaller(cwd=self.remote_repository1)
    call("git commit -av -m new_commit".split())
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    self.assertTrue(rev_list[0].startswith('rep0=2-'))
    self.assertTrue(rev_list[1].startswith('rep1=3-'))
    self.assertEquals(2, len(node_test_suite.vcs_repository_list))
    for vcs_repository in node_test_suite.vcs_repository_list:
      self.assertTrue(os.path.exists(vcs_repository['repository_path']))

  def test_05b_changeRepositoryBranch(self):
    """
    It could happen that the branch is changed for a repository. Testnode must
    be able to reset correctly the branch
    """
    commit_dict = self.generateTestRepositoryList(add_third_repository=True)
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite, add_third_repository=True)
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    self.assertEquals(3, len(rev_list))
    self.assertEquals(3, len(node_test_suite.vcs_repository_list))
    rep2_clone_path = [x['repository_path'] for x in \
                       node_test_suite.vcs_repository_list \
                       if x['repository_path'].endswith("rep2")][0]
    call = self.getCaller(cwd=rep2_clone_path)
    output = call("git branch".split()).strip()
    self.assertTrue("* foo" in output.split('\n'))
    vcs_repository_info = node_test_suite.vcs_repository_list[0]
    self.assertEquals(vcs_repository_info['repository_id'], 'rep2')
    self.assertEquals(vcs_repository_info['branch'], 'foo')
    # change it to master
    vcs_repository_info['branch'] = 'master'
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    output = call("git branch".split()).strip()
    print output
    self.assertTrue("* master" in output.split('\n'))
    # Add a third branch on remote, make sure we could switch to it
    remote_call = self.getCaller(cwd=self.remote_repository2)
    output = remote_call('git checkout master -b bar'.split())
    vcs_repository_info['branch'] = 'bar'
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    output = call("git branch".split()).strip()
    self.assertTrue("* bar" in output.split('\n'))

  def test_06_checkRevision(self):
    """
    Check if we are able to restore older commit hash if master decide so
    """
    commit_dict = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    def getRepInfo(count=0, hash=0):
      assert count or hash
      info_list = []
      for vcs_repository in node_test_suite.vcs_repository_list:
        call = self.getCaller(cwd=vcs_repository['repository_path'])
        if count:
          info_list.append(
            call("git rev-list --topo-order --count HEAD".split()).strip())
        if hash:
          info_list.append(
            call("git log -n1 --format=%H".split()).strip())
      return info_list
    self.assertEquals(['2', '2'], getRepInfo(count=1))
    self.assertEquals([commit_dict['rep0'][0][0],commit_dict['rep1'][0][0]],
                      getRepInfo(hash=1))
    class TestResult(object):
      pass
    test_result = TestResult()
    # for test result to be one commit late for rep1 to force testnode to
    # reset tree to older version
    test_result.revision = 'rep0=2-%s,rep1=1-%s' % (commit_dict['rep0'][0][0],
                                                    commit_dict['rep1'][1][0])
    test_node.checkRevision(test_result, node_test_suite)
    expected_count_list = ['2', '1']
    self.assertEquals(['2', '1'], getRepInfo(count=1))
    self.assertEquals([commit_dict['rep0'][0][0],commit_dict['rep1'][1][0]],
                      getRepInfo(hash=1))

  def test_07_checkExistingTestSuite(self):
    test_node = self.getTestNode()
    test_suite_data = self.getTestSuiteData(add_third_repository=True)
    self.assertEquals([], os.listdir(self.working_directory))
    test_node.checkOldTestSuite(test_suite_data)
    self.assertEquals([], os.listdir(self.working_directory))
    os.mkdir(os.path.join(self.working_directory, 'foo'))
    self.assertEquals(['foo'], os.listdir(self.working_directory))
    test_node.checkOldTestSuite(test_suite_data)
    self.assertEquals(['foo'], os.listdir(self.working_directory))
    os.mkdir(os.path.join(self.working_directory, 'bar'))
    self.assertEquals(set(['bar','foo']),
                      set(os.listdir(self.working_directory)))
    test_node.checkOldTestSuite(test_suite_data)
    self.assertEquals(['foo'], os.listdir(self.working_directory))

  def test_08_getSupportedParamaterSet(self):
    original_spawn = ProcessManager.spawn
    try:
      def get_help(self, *args, **kw):
        return {'stdout': """My Program
                  --foo  foo
                  --bar  bar"""}
      ProcessManager.spawn = get_help
      process_manager = ProcessManager(log=None)
      parameter_list = ['--foo', '--baz']
      expected_suported_parameter_set = set(['--foo'])
      supported_parameter_set = process_manager.getSupportedParameterSet(
                                 "dummy_program_path", parameter_list)
      self.assertEquals(expected_suported_parameter_set, supported_parameter_set)
    finally:
      ProcessManager.spawn = original_spawn

  def test_09_runTestSuite(self):
    """
    Check parameters passed to runTestSuite
    Also make sure that --firefox_bin and --xvfb_bin are passed when needed
    """
    original_getSupportedParameter = ProcessManager.getSupportedParameterSet
    original_spawn = ProcessManager.spawn
    try:
      def _createPath(path_to_create, end_path):
        os.makedirs(path_to_create)
        return os.close(os.open(os.path.join(path_to_create,
                                 end_path),os.O_CREAT))
      def get_parameters(self, *args, **kw):
        call_parameter_list.append({'args': [x for x in args], 'kw':kw})
      def patch_getSupportedParameterSet(self, run_test_suite_path, parameter_list,):
       if '--firefox_bin' and '--xvfb_bin' in parameter_list:
         return set(['--firefox_bin','--xvfb_bin'])
       else:
         return []
      test_node = self.getTestNode()
      test_node.slapos_controler = SlapOSControler(self.working_directory,
                                               test_node.config, self.log)
      node_test_suite = test_node.getNodeTestSuite('foo')
      self.updateNodeTestSuiteData(node_test_suite)
      node_test_suite.revision = 'dummy'
      run_test_suite_path = _createPath(
          os.path.join(test_node.slapos_controler.instance_root,'a/bin'),'runTestSuite')
      def checkRunTestSuiteParameters(additional_parameter_list=None):
        ProcessManager.getSupportedParameterSet = patch_getSupportedParameterSet
        ProcessManager.spawn = get_parameters
        test_node.runTestSuite(node_test_suite,"http://foo.bar")
        expected_parameter_list = ['%s/a/bin/runTestSuite'
             %(test_node.slapos_controler.instance_root), '--test_suite', 'Foo', '--revision',
             'dummy', '--test_suite_title', 'Foo-Test', '--node_quantity', 3, '--master_url',
             'http://foo.bar']
        if additional_parameter_list:
          expected_parameter_list.extend(additional_parameter_list)
        self.assertEqual(call_parameter_list[0]['args'], expected_parameter_list)
      call_parameter_list = []
      checkRunTestSuiteParameters()
      _createPath(os.path.join(test_node.config['slapos_directory'], 'soft/a/parts/firefox'),'firefox-slapos')
      _createPath(os.path.join(test_node.config['slapos_directory'], 'soft/a/parts/xserver/bin'),'Xvfb')
      call_parameter_list = []
      checkRunTestSuiteParameters(additional_parameter_list=['--firefox_bin',
        '%s/soft/a/parts/firefox/firefox-slapos'
         %(test_node.config['slapos_directory']),
        '--xvfb_bin',
        '%s/soft/a/parts/xserver/bin/Xvfb'
          %(test_node.config['slapos_directory'])])
    finally:
      ProcessManager.getSupportedParameterSet   = original_getSupportedParameter
      ProcessManager.spawn = original_spawn

  def test_10_prepareSlapOS(self):
    test_node = self.getTestNode()
    test_node_slapos = SlapOSInstance()
    node_test_suite = test_node.getNodeTestSuite('foo')
    node_test_suite.edit(working_directory=self.working_directory)
    status_dict = {"status_code" : 0}
    global call_list
    call_list = []
    class Patch:
      def __init__(self, method_name, status_code=0):
        self.method_name = method_name
        self.status_code = status_code
      def __call__(self, *args, **kw):
        global call_list
        call_list.append({"method_name": self.method_name,
                         "args": [x for x in args],
                          "kw": kw})
        return {"status_code": self.status_code}
    SlapOSControler.initializeSlapOSControler = Patch("initializeSlapOSControler")
    SlapOSControler.runSoftwareRelease = Patch("runSoftwareRelease")
    SlapOSControler.runComputerPartition = Patch("runComputerPartition")
    test_node.prepareSlapOSForTestNode(test_node_slapos)
    self.assertEquals(["initializeSlapOSControler", "runSoftwareRelease"],
                      [x["method_name"] for x in call_list])
    call_list = []
    test_node.prepareSlapOSForTestSuite(node_test_suite)
    self.assertEquals(["initializeSlapOSControler", "runSoftwareRelease",
                       "runComputerPartition"],
                      [x["method_name"] for x in call_list])
    call_list = []
    SlapOSControler.runSoftwareRelease = Patch("runSoftwareRelease", status_code=1)
    self.assertRaises(SubprocessError, test_node.prepareSlapOSForTestSuite,
                     node_test_suite)

  def test_11_run(self):
    def doNothing(self, *args, **kw):
        pass
    test_self = self
    test_result_path_root = os.path.join(test_self._temp_dir,'test/results')
    os.makedirs(test_result_path_root)
    global counter
    counter = 0
    def patch_startTestSuite(self,test_node_title):
      global counter
      config_list = []
      def _checkExistingTestSuite(reference_set):
        test_self.assertEquals(set(reference_set),
                    set(os.listdir(test_node.config["working_directory"])))
        for x in reference_set:
          test_self.assertTrue(os.path.exists(os.path.join(
                               test_node.config["working_directory"],x)),True)
      if counter == 0:
        config_list.append(test_self.getTestSuiteData(reference='foo')[0])
        config_list.append(test_self.getTestSuiteData(reference='bar')[0])
      elif counter == 1:
        _checkExistingTestSuite(set(['foo']))
        config_list.append(test_self.getTestSuiteData(reference='bar')[0])
        config_list.append(test_self.getTestSuiteData(reference='foo')[0])
      elif counter == 2:
        _checkExistingTestSuite(set(['foo','bar']))
        config_list.append(test_self.getTestSuiteData(reference='foo')[0])
        config_list.append(test_self.getTestSuiteData(reference='qux')[0])
      elif counter == 3:
        _checkExistingTestSuite(set(['foo','qux']))
        config_list.append(test_self.getTestSuiteData(reference='foox')[0])
      elif counter == 4:
        _checkExistingTestSuite(set(['foox']))
        config_list.append(test_self.getTestSuiteData(reference='bax')[0])
      elif counter == 5:
        _checkExistingTestSuite(set(['bax']))
        raise StopIteration
      counter += 1
      return json.dumps(config_list)
    def patch_createTestResult(self, revision, test_name_list, node_title,
            allow_restart=False, test_title=None, project_title=None):
      global counter
      # return no test to check if run method will run the next test suite
      if counter == 3 and project_title != 'qux':
        result = None
      else:
        test_result_path = os.path.join(test_result_path_root, test_title)
        result =  TestResultProxy(self._proxy, self._retry_time,
                self._logger, test_result_path, node_title, revision)
      return result
    original_sleep = time.sleep
    time.sleep = doNothing
    self.generateTestRepositoryList()
    original_startTestSuite = TaskDistributor.startTestSuite
    TaskDistributor.startTestSuite = patch_startTestSuite
    original_createTestResult = TaskDistributionTool.createTestResult
    TaskDistributionTool.createTestResult = patch_createTestResult
    test_node = self.getTestNode()
    original_prepareSlapOS = test_node._prepareSlapOS
    test_node._prepareSlapOS = doNothing
    original_runTestSuite = test_node.runTestSuite
    test_node.runTestSuite = doNothing
    SlapOSControler.initializeSlapOSControler = doNothing
    test_node.run()
    self.assertEquals(5, counter)
    time.sleep = original_sleep
    TaskDistributor.startTestSuite = original_startTestSuite
    TaskDistributionTool.createTestResult = original_createTestResult
    test_node._prepareSlapOS = original_prepareSlapOS
    test_node.runTestSuite = original_runTestSuite

  def test_12_spawn(self):
    def _checkCorrectStatus(expected_status,*args):
      result = process_manager.spawn(*args)
      self.assertEqual(result['status_code'], expected_status)
    process_manager = ProcessManager(log=self.log, max_timeout=1)
    _checkCorrectStatus(0, *['sleep','0'])
    # We must make sure that if the command is too long that
    # it will be automatically killed
    self.assertRaises(SubprocessError, process_manager.spawn, 'sleep','3')

  def test_13_SlaposControlerResetSoftware(self):
    test_node = self.getTestNode()
    controler = SlapOSControler(self.working_directory,
                                test_node.config, self.log)
    os.mkdir(controler.software_root)
    file_name = 'AC_Ra\xc3\xadzertic\xc3\xa1ma'
    non_ascii_file = open(os.path.join(controler.software_root, file_name), 'w')
    non_ascii_file.close()
    self.assertEquals([file_name], os.listdir(controler.software_root))
    controler._resetSoftware()
    self.assertEquals([], os.listdir(controler.software_root))

  def test_14_createFolder(self):
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    node_test_suite.edit(working_directory=self.working_directory)
    folder = node_test_suite.test_suite_directory
    self.assertEquals(False, os.path.exists(folder))
    createFolder(folder)
    self.assertEquals(True, os.path.exists(folder))
    to_drop_path = os.path.join(folder, 'drop')
    to_drop = open(to_drop_path, 'w')
    to_drop.close()
    self.assertEquals(True, os.path.exists(to_drop_path))
    createFolder(folder, clean=True)
    self.assertEquals(False, os.path.exists(to_drop_path))

  def test_15_suite_log_directory(self):
    def doNothing(self, *args, **kw):
        pass
    test_self = self
    test_result_path_root = os.path.join(test_self._temp_dir,'test/results')
    os.makedirs(test_result_path_root)
    global counter
    counter = 0
    def patch_startTestSuite(self,test_node_title):
      global counter
      config_list = [test_self.getTestSuiteData(reference='aa')[0],
                     test_self.getTestSuiteData(reference='bb')[0]]
      if counter in (1, 2):
        config_list.reverse()
      elif counter == 3:
        raise StopIteration
      counter += 1
      return json.dumps(config_list)
    def patch_createTestResult(self, revision, test_name_list, node_title,
            allow_restart=False, test_title=None, project_title=None):
      test_result_path = os.path.join(test_result_path_root, test_title)
      result = TestResultProxy(self._proxy, self._retry_time,
               self._logger, test_result_path, node_title, revision)
      return result
    def checkTestSuite(test_node):
      test_node.node_test_suite_dict
      rand_part_set = set()
      self.assertEquals(2, len(test_node.node_test_suite_dict))
      assert(test_node.suite_log is not None)
      assert(isinstance(test_node.suite_log, types.MethodType))
      for ref, suite in test_node.node_test_suite_dict.items():
        self.assertTrue('var/log/testnode/%s' % suite.reference in \
                         suite.suite_log_path,
                         "Incorrect suite log path : %r" % suite.suite_log_path)
        assert(suite.suite_log_path.endswith('suite.log'))
        m = re.match('.*\-(.*)\/suite.log', suite.suite_log_path)
        rand_part = m.groups()[0]
        assert(len(rand_part) == 32)
        assert(rand_part not in rand_part_set)
        rand_part_set.add(rand_part)
        suite_log = open(suite.suite_log_path, 'r')
        self.assertEquals(1, len([x for x in suite_log.readlines() \
                              if x.find("Activated logfile")>=0]))

    original_sleep = time.sleep
    time.sleep = doNothing
    self.generateTestRepositoryList()
    original_startTestSuite = TaskDistributor.startTestSuite
    TaskDistributor.startTestSuite = patch_startTestSuite
    original_createTestResult = TaskDistributionTool.createTestResult
    TaskDistributionTool.createTestResult = patch_createTestResult
    test_node = self.getTestNode()
    original_prepareSlapOS = test_node._prepareSlapOS
    test_node._prepareSlapOS = doNothing
    original_runTestSuite = test_node.runTestSuite
    test_node.runTestSuite = doNothing
    SlapOSControler.initializeSlapOSControler = doNothing
    test_node.run()
    self.assertEquals(counter, 3)
    checkTestSuite(test_node)
    time.sleep = original_sleep
    TaskDistributor.startTestSuite = original_startTestSuite
    TaskDistributionTool.createTestResult = original_createTestResult
    test_node._prepareSlapOS = original_prepareSlapOS
    test_node.runTestSuite = original_runTestSuite

  def test_16_cleanupLogDirectory(self):
    # Make sure that we are able to cleanup old log folders
    test_node = self.getTestNode()
    def check(file_list):
      log_directory_dir = os.listdir(self.log_directory)
      self.assertTrue(set(file_list).issubset(
           set(log_directory_dir)),
           "%r not contained by %r" % (file_list, log_directory_dir))
    check([])
    os.mkdir(os.path.join(self.log_directory, 'ab-llzje'))
    a_file = open(os.path.join(self.log_directory, 'a_file'), 'w')
    a_file.close()
    check(set(['ab-llzje', 'a_file']))
    # default log file time is 15 days, so nothing is going to be deleted
    test_node._cleanupLog()
    check(set(['ab-llzje', 'a_file']))
    # then we set keep time to 0, folder will be deleted
    test_node.max_log_time = 0
    test_node._cleanupLog()
    check(set(['a_file']))

  def test_17_cleanupTempDirectory(self):
    # Make sure that we are able to cleanup old temp folders
    test_node = self.getTestNode()
    temp_directory = self.system_temp_folder
    def check(file_list):
      directory_dir = os.listdir(temp_directory)
      self.assertTrue(set(file_list).issubset(
           set(directory_dir)),
           "%r not contained by %r" % (file_list, directory_dir))
    check([])
    os.mkdir(os.path.join(temp_directory, 'buildoutA'))
    os.mkdir(os.path.join(temp_directory, 'something'))
    os.mkdir(os.path.join(temp_directory, 'tmpC'))
    check(set(['buildoutA', 'something', 'tmpC']))
    # default log file time is 15 days, so nothing is going to be deleted
    test_node._cleanupTemporaryFiles()
    check(set(['buildoutA', 'something', 'tmpC']))
    # then we set keep time to 0, folder will be deleted
    test_node.max_temp_time = 0
    test_node._cleanupTemporaryFiles()
    check(set(['something']))

  def test_18_resetSoftwareAfterManyBuildFailures(self):
    """
    Check that after several building failures that the software is resetted
    """
    initial_initializeSlapOSControler = \
      SlapOSControler.initializeSlapOSControler
    initial_runSoftwareRelease = SlapOSControler.runSoftwareRelease
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    init_call_kw_list = []
    def initializeSlapOSControler(self, **kw):
      init_call_kw_list.append(kw)
    def runSoftwareRelease(self, *args, **kw):
      return {"status_code": 1}
    SlapOSControler.initializeSlapOSControler = initializeSlapOSControler
    SlapOSControler.runSoftwareRelease = runSoftwareRelease
    def callPrepareSlapOS():
      test_node._prepareSlapOS(self.working_directory, node_test_suite,
         test_node.log, create_partition=0)
    def callRaisingPrepareSlapos():
      self.assertRaises(SubprocessError, callPrepareSlapOS)
    self.assertEquals(node_test_suite.retry_software_count, 0)
    for x in xrange(0,11):
      callRaisingPrepareSlapos()
    self.assertEquals(len(init_call_kw_list), 11)
    self.assertEquals(init_call_kw_list[-1]['reset_software'], False)
    self.assertEquals(node_test_suite.retry_software_count, 11)
    callRaisingPrepareSlapos()
    self.assertEquals(init_call_kw_list[-1]['reset_software'], True)
    self.assertEquals(node_test_suite.retry_software_count, 1)
    callRaisingPrepareSlapos()
    self.assertEquals(init_call_kw_list[-1]['reset_software'], False)
    self.assertEquals(node_test_suite.retry_software_count, 2)
    SlapOSControler.initializeSlapOSControler = \
      initial_initializeSlapOSControler
    SlapOSControler.runSoftwareRelease = initial_runSoftwareRelease
