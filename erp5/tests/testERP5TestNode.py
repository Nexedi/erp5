from unittest import TestCase

import sys
sys.path.extend([
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/slapos.cookbook-0.65-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/zc.recipe.egg-1.3.2-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/zc.buildout-1.6.0_dev_SlapOS_010-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/xml_marshaller-0.9.7-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/slapos.core-0.28.5-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/inotifyx-0.2.0-py2.7-linux-x86_64.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/setuptools-0.6c12dev_r88846-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/netaddr-0.7.10-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/develop-eggs/lxml-2.3.6-py2.7-linux-x86_64.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/PyXML-0.8.4-py2.7-linux-x86_64.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/zope.interface-4.0.1-py2.7-linux-x86_64.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/supervisor-3.0a12-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/netifaces-0.8-py2.7-linux-x86_64.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/Flask-0.9-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/meld3-0.6.8-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/Jinja2-2.6-py2.7.egg',
    '/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/eggs/Werkzeug-0.8.3-py2.7.egg',
    ])

from erp5.util.testnode import TestNode
from erp5.util.testnode.ProcessManager import ProcessManager
from erp5.util.testnode.SlapOSControler import SlapOSControler
import os
import shutil
import subprocess
import tempfile

class ERP5TestNode(TestCase):

  def setUp(self):
    self._temp_dir = tempfile.mkdtemp()
    self.working_directory = os.path.join(self._temp_dir, 'testnode')
    self.slapos_directory = os.path.join(self._temp_dir, 'slapos')
    self.test_suite_directory = os.path.join(self._temp_dir,'test_suite')
    self.remote_repository0 = os.path.join(self._temp_dir, 'rep0')
    self.remote_repository1 = os.path.join(self._temp_dir, 'rep1')
    self.remote_repository2 = os.path.join(self._temp_dir, 'rep2')
    os.mkdir(self.working_directory)
    os.mkdir(self.slapos_directory)
    os.mkdir(self.test_suite_directory)
    os.mkdir(self.remote_repository0)
    os.mkdir(self.remote_repository1)
    os.mkdir(self.remote_repository2)

  def tearDown(self):
    shutil.rmtree(self._temp_dir, True)

  def getTestNode(self):
    def log(*args):
      for arg in args:
        print "TESTNODE LOG : %r" % (arg,)
    # XXX how to get property the git path ?
    config = {}
    config["git_binary"] = "/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/parts/git/bin/git"
    config["slapos_directory"] = config["working_directory"] = self.working_directory
    config["node_quantity"] = 3
    config["test_suite_directory"] = self.test_suite_directory

    return TestNode(log, config)

  def getTestSuiteData(self, add_third_repository=False):
    data = [{
       "test_suite": "Foo",
       "project_title": "Foo",
       "test_suite_title": "Foo-Test",
       "test_suite_reference": "foo",
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
      call("touch first_file".split())
      call("git add first_file".split())
      call("git commit -v -m first_commit".split() + ['--author="a b <a@b.c>"'])
      my_file = open(os.path.join(repository_path, 'first_file'), 'w')
      my_file.write("initial_content%i" % i)
      my_file.close()
      call("git commit -av -m next_commit".split() + ['--author="a b <a@b.c>"'])
      output = call(['git', 'log', '--format=%H %s'])
      output_line_list = output.split("\n")
      self.assertEquals(3, len(output_line_list))
      # remove additional return line
      output_line_list = output_line_list[0:2]
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
    call("git commit -av -m new_commit".split() + ['--author="a b <a@b.c>"'])
    rev_list = test_node.getAndUpdateFullRevisionList(node_test_suite)
    self.assertTrue(rev_list[0].startswith('rep0=2-'))
    self.assertTrue(rev_list[1].startswith('rep1=3-'))
    self.assertEquals(2, len(node_test_suite.vcs_repository_list))
    for vcs_repository in node_test_suite.vcs_repository_list:
      self.assertTrue(os.path.exists(vcs_repository['repository_path']))

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

  def test_07_checkOldTestSuite(self):
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
                                             test_node.config,test_node.log)
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
