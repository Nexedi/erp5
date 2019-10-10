import unittest
from unittest import TestCase
from contextlib import contextmanager

from erp5.util.testnode import logger
from erp5.util.testnode.testnode import TestNode, test_type_registry
from erp5.util.testnode.NodeTestSuite import SlapOSInstance, NodeTestSuite
from erp5.util.testnode.ProcessManager import ProcessManager, SubprocessError
from erp5.util.testnode.Updater import Updater

from erp5.util.testnode.SlapOSMasterCommunicator import SlapOSMasterCommunicator
from erp5.util.testnode.SlapOSControler import SlapOSControler
from erp5.util.testnode.SlapOSControler import createFolder

from erp5.util.taskdistribution import TaskDistributor
from erp5.util.taskdistribution import TestResultProxy
import argparse
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import json
import time
import re

@contextmanager
def dummySuiteLog(_):
  yield

class ERP5TestNode(TestCase):

  _handler = logging.StreamHandler(sys.stdout)
  _handler.setFormatter(logging.Formatter('TESTNODE LOG: %(message)s'))

  def setUp(self):
    self._temp_dir = tempfile.mkdtemp()
    self.working_directory = os.path.join(self._temp_dir, 'testnode')
    self.slapos_directory = os.path.join(self._temp_dir, 'slapos')
    self.software_directory = os.path.join(self._temp_dir, 'software_directory')
    self.test_suite_directory = os.path.join(self._temp_dir,'test_suite')
    self.environment = os.path.join(self._temp_dir,'environment')
    self.log_directory = os.path.join(self._temp_dir,'var/log/testnode')
    self.log_file = os.path.join(self.log_directory,'test.log')
    self.remote_repository0 = os.path.join(self._temp_dir, 'rep0')
    self.remote_repository1 = os.path.join(self._temp_dir, 'rep1')
    self.remote_repository2 = os.path.join(self._temp_dir, 'rep2')
    self.remote_repository_broken = os.path.join(self._temp_dir, 'broken')
    self.system_temp_folder = os.path.join(self._temp_dir,'tmp')
    os.mkdir(self.working_directory)
    os.mkdir(self.slapos_directory)
    os.mkdir(self.test_suite_directory)
    os.mkdir(self.software_directory)
    os.mkdir(self.environment)
    os.mkdir(self.system_temp_folder)
    os.makedirs(self.log_directory)
    os.close(os.open(self.log_file,os.O_CREAT))
    os.mkdir(self.remote_repository0)
    os.mkdir(self.remote_repository1)
    os.mkdir(self.remote_repository2)
    logging.getLogger().addHandler(self._handler)

  def tearDown(self):
    shutil.rmtree(self._temp_dir, True)
    logging.getLogger().removeHandler(self._handler)

  def getTestNode(self):
    # XXX how to get property the git path ?
    config = {}
    config["git_binary"] = "git"
    config["slapos_directory"] = self.slapos_directory
    config["working_directory"] = self.working_directory
    config["software_directory"] = self.software_directory
    config["node_quantity"] = '3'
    config["test_suite_directory"] = self.test_suite_directory
    config["environment"] = self.environment
    config["log_directory"] = self.log_directory
    config["log_file"] = self.log_file
    config["test_suite_master_url"] = None
    config["hateoas_slapos_master_url"] = None
    config["test_node_title"] = "Foo-Test-Node"
    config["system_temp_folder"] = self.system_temp_folder
    config["computer_id"] = "COMP-TEST"
    config["server_url"] = "http://foo.bar"
    config["httpd_ip"] = "ff:ff:ff:ff:ff:ff:ff:ff"
    config["httpd_software_access_port"] = "9080"
    config["frontend_url"] = "http://frontend/"
    config["software_list"] = ["foo", "bar"]
    config["slapos_binary"] = "/opt/slapgrid/HASH/bin/slapos"
    config["srv_directory"] = "srv_directory"

    testnode = TestNode(config)
    # By default, keep suite logs to stdout for easier debugging
    # (stdout/stderr are automatically reported to ERP5).
    # This is unset by test methods that check normal suite logging.
    testnode.suiteLog = dummySuiteLog
    return testnode

  def getTestSuiteData(self, add_third_repository=False,
                       add_broken_repository=False, reference="foo"):
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
    if add_broken_repository:
      data[0]['vcs_repository_list'].append(
            {'url': self.remote_repository_broken,
             'buildout_section_id': 'rep2',
             'branch': 'foo'})
    return data

  def updateNodeTestSuiteData(self, node_test_suite,
                              add_third_repository=False,
                              add_broken_repository=False):
    """
    Update from zero/Regenerate the testsuite
    """
    node_test_suite.edit(
       **self.getTestSuiteData(add_third_repository=add_third_repository,
                               add_broken_repository=add_broken_repository)[0])

  def getCaller(self, **kw):
    class Caller(object):

      def __init__(self, **kw):
        self.__dict__.update(**kw)

      def __call__(self, command):
        return subprocess.check_output(command, universal_newlines=True,
                                       **self.__dict__)
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
      self.assertEqual(2, len(output_line_list))
      expected_commit_subject_list = ["next_commit", "first_commit"]
      commit_subject_list = [x.split()[1] for x in output_line_list]
      self.assertEqual(expected_commit_subject_list, commit_subject_list)
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
    self.assertEqual(0, node_test_suite.retry_software_count)
    node_test_suite.retry_software_count = 2
    self.assertIs(node_test_suite, test_node.getNodeTestSuite('foo'))
    self.assertEqual(2, node_test_suite.retry_software_count)
    del test_node.node_test_suite_dict['foo']
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.assertEqual(0, node_test_suite.retry_software_count)

  def test_02_NodeTestSuiteWorkingDirectory(self):
    """
    Make sure we extend the working path with the node_test_suite reference
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.assertEqual("%s/foo" % self.working_directory,
                      node_test_suite.working_directory)
    self.assertEqual("%s/foo/test_suite" % self.working_directory,
                      node_test_suite.test_suite_directory)

  def test_03_NodeTestSuiteCheckDataAfterEdit(self):
    """
    When a NodeTestSuite instance is edited, the method _checkData
    analyse properties and add new ones
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    self.assertEqual(2, len(node_test_suite.vcs_repository_list))
    repository_path_list = []
    for vcs_repository in node_test_suite.vcs_repository_list:
      repository_path_list.append(vcs_repository['repository_path'])
    expected_list = ["%s/rep0" % node_test_suite.working_directory,
                     "%s/rep1" % node_test_suite.working_directory]
    self.assertEqual(expected_list, repository_path_list)

  def test_04_constructProfile(self, my_test_type='UnitTest'):
    """
    Check if the software profile is correctly generated
    """
    test_node = self.getTestNode()
    test_node.test_suite_portal = TaskDistributor
    test_node.test_suite_portal.getTestNode = TaskDistributor.getTestType
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite, add_third_repository=True)
    node_test_suite.revision_list = (('rep1', (1234, 'azerty')),
                                     ('rep2', (3456, 'qwerty')))
    test_node.constructProfile(node_test_suite,my_test_type)
    self.assertEqual("%s/software.cfg" % (node_test_suite.working_directory,),
                      node_test_suite.custom_profile_path)
    profile = open(node_test_suite.custom_profile_path, 'r')
    if my_test_type=='UnitTest':
      expected_profile = """\
[buildout]
extends = %(temp_dir)s/testnode/foo/rep0/software.cfg

[rep1]
repository = %(temp_dir)s/testnode/foo/rep1
branch = master
revision =
develop = false
shared = true

[rep2]
repository = %(temp_dir)s/testnode/foo/rep2
branch = foo
revision =
develop = false
shared = true
""" % {'temp_dir': self._temp_dir}
    else:
      revision1 = "azerty"
      revision2 = "qwerty"
      expected_profile = """\
[buildout]
extends = %(temp_dir)s/testnode/foo/rep0/software.cfg

[rep1]
repository = %(temp_dir)s/rep1
revision = %(revision1)s
ignore-ssl-certificate = true
develop = false
shared = true

[rep2]
repository = %(temp_dir)s/rep2
revision = %(revision2)s
ignore-ssl-certificate = true
develop = false
shared = true
""" % {'temp_dir': self._temp_dir, 'revision1': revision1, 'revision2': revision2}
    self.assertEqual(expected_profile, profile.read())
    profile.close()

  def getAndUpdateFullRevisionList(self, test_node, node_test_suite):
    if test_node.updateRevisionList(node_test_suite):
      return node_test_suite.revision.split(',')

  def test_05_updateRevisionList(self):
    """
    Check if we clone correctly repositories and get right revisions
    """
    commit_dict = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(2, len(rev_list))
    self.assertEqual(rev_list[0], 'rep0=2-%s' % commit_dict['rep0'][0][0])
    self.assertEqual(rev_list[1], 'rep1=2-%s' % commit_dict['rep1'][0][0])
    my_file = open(os.path.join(self.remote_repository1, 'first_file'), 'w')
    my_file.write("next_content")
    my_file.close()
    call = self.getCaller(cwd=self.remote_repository1)
    call("git commit -av -m new_commit".split())
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertTrue(rev_list[0].startswith('rep0=2-'))
    self.assertTrue(rev_list[1].startswith('rep1=3-'))
    self.assertEqual(2, len(node_test_suite.vcs_repository_list))
    for vcs_repository in node_test_suite.vcs_repository_list:
      self.assertTrue(os.path.exists(vcs_repository['repository_path']))

  def test_05b_changeRepositoryBranch(self, my_test_type='UnitTest'):
    """
    It could happen that the branch is changed for a repository. Testnode must
    be able to reset correctly the branch
    """
    commit_dict = self.generateTestRepositoryList(add_third_repository=True)
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite, add_third_repository=True)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(3, len(rev_list))
    self.assertEqual(3, len(node_test_suite.vcs_repository_list))
    rep2_clone_path = [x['repository_path'] for x in \
                       node_test_suite.vcs_repository_list \
                       if x['repository_path'].endswith("rep2")][0]
    call = self.getCaller(cwd=rep2_clone_path)
    output = call("git branch".split()).strip()
    self.assertTrue("* foo" in output.split('\n'))
    vcs_repository_info = node_test_suite.vcs_repository_list[0]
    self.assertEqual(vcs_repository_info['repository_id'], 'rep2')
    self.assertEqual(vcs_repository_info['branch'], 'foo')
    # change it to master
    vcs_repository_info['branch'] = 'master'
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    output = call("git branch".split()).strip()
    print(output)
    self.assertTrue("* master" in output.split('\n'))
    # Add a third branch on remote, make sure we could switch to it
    remote_call = self.getCaller(cwd=self.remote_repository2)
    output = remote_call('git checkout master -b bar'.split())
    vcs_repository_info['branch'] = 'bar'
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    output = call("git branch".split()).strip()
    self.assertTrue("* bar" in output.split('\n'))
    # Add a fourth branch on remote, make sure we could switch to it
    # this time the branch name is a substring of previous one (we had
    # failure is such case at some point)
    remote_call = self.getCaller(cwd=self.remote_repository2)
    output = remote_call('git checkout master -b ba'.split())
    vcs_repository_info['branch'] = 'ba'
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    output = call("git branch".split()).strip()
    self.assertTrue("* ba" in output.split('\n'))

  def test_05c_changeRepositoryUrl(self):
    """
    It could happen that the url is changed for a repository (new place, or
    change of username and password). testnode must be able to erase and clone
    again the repository
    """
    commit_dict = self.generateTestRepositoryList(add_third_repository=True)
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(2, len(rev_list))
    self.assertEqual(2, len(node_test_suite.vcs_repository_list))
    # patch deleteRepository to make sure it will be called once for the wrong
    # repos, and not for the repos which has not changed
    deleted_repository_path_list = []
    original_deleteRepository = Updater.deleteRepository
    try:
      def deleteRepository(self):
        deleted_repository_path_list.append(self.repository_path)
        original_deleteRepository(self)
      Updater.deleteRepository = deleteRepository
      # change the url of the first repository
      vcs_repository_info = node_test_suite.vcs_repository_list[0]
      vcs_repository_info["url"] = self.remote_repository2
      rep0_clone_path = [x['repository_path'] for x in \
                         node_test_suite.vcs_repository_list \
                         if x['repository_path'].endswith("rep0")][0]
      call = self.getCaller(cwd=rep0_clone_path)
      self.assertEqual(call("git config --get remote.origin.url".split()).strip(),
                        self.remote_repository0)
      rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
      self.assertEqual(call("git config --get remote.origin.url".split()).strip(),
                        self.remote_repository2)
      self.assertEqual([rep0_clone_path], deleted_repository_path_list)
    finally:
      Updater.deleteRepository = original_deleteRepository

  def test_05d_LocalModificationOnRepository(self):
    """
    It could happen that there is local modification to to either bug of
    git or any manual operation.
    Testnode must be able reset the repository to make sure we have no failures
    when updating repository
    """
    commit_dict = self.generateTestRepositoryList(add_third_repository=True)
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(2, len(rev_list))
    self.assertEqual(2, len(node_test_suite.vcs_repository_list))
    rep0_clone_path = [x['repository_path'] for x in \
                   node_test_suite.vcs_repository_list \
                   if x['repository_path'].endswith("rep0")][0]
    my_file = open(os.path.join(rep0_clone_path, 'first_file'), 'w')
    my_file.write("next_content")
    my_file.close()
    # make sure code still works
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(2, len(rev_list))
    self.assertEqual(2, len(node_test_suite.vcs_repository_list))
    # and check local change was resetted
    my_file = open(os.path.join(rep0_clone_path, 'first_file'), 'r')
    self.assertEqual("initial_content0", my_file.read())
    my_file.close()

  def test_05e_IgnoringIncorrectRepository(self):
    """
    If someone add a test suite with a bad url for git repository (or wrong
    crendentials), the testnode should not block forever and should work on
    other test suites. This method should be able to run
    """
    commit_dict = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite, add_broken_repository=True)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(None, rev_list)

  def test_05f_ResetCorruptedRepository(self):
    """
    It could happens that repository are corrupted, like when server is restarted
    in the middle of a git checkout. So make sure testnode remove repositories
    that are not working any longer.

    In this test, we cause an artificial corruption by truncating git
    repository's index, then we call updateRevisionList to check that it can
    recover from this corruption.
    """
    commit_dict = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertTrue(rev_list is not None)
    rep0_clone_path = [x['repository_path'] for x in \
                   node_test_suite.vcs_repository_list \
                   if x['repository_path'].endswith("rep0")][0]
    # simulate a data corruption on rep0's index
    with open(os.path.join(rep0_clone_path, '.git', 'index'), 'ab') as index_file:
      index_file.seek(10, os.SEEK_END)
      index_file.truncate()
    # we get rev list with corrupted repository, we get None, but in the same
    # time the bad repository is deleted
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertEqual(None, rev_list)
    # So next update should go fine
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
    self.assertTrue(rev_list is not None)

  def test_06_checkRevision(self):
    """
    Check if we are able to restore older commit hash if master decide so
    """
    commit_dict = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    rev_list = self.getAndUpdateFullRevisionList(test_node, node_test_suite)
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
    self.assertEqual(['2', '2'], getRepInfo(count=1))
    self.assertEqual([commit_dict['rep0'][0][0],commit_dict['rep1'][0][0]],
                      getRepInfo(hash=1))
    class TestResult(object):
      revision = NodeTestSuite.revision
    test_result = TestResult()
    # for test result to be one commit late for rep1 to force testnode to
    # reset tree to older version
    test_result.revision_list = (('rep0', (2, commit_dict['rep0'][0][0])),
                                 ('rep1', (1, commit_dict['rep1'][1][0])))
    test_node.checkRevision(test_result, node_test_suite)
    self.assertEqual(['2', '1'], getRepInfo(count=1))
    self.assertEqual([commit_dict['rep0'][0][0],commit_dict['rep1'][1][0]],
                      getRepInfo(hash=1))

  def test_07_checkExistingTestSuite(self):
    test_node = self.getTestNode()
    test_suite_data = self.getTestSuiteData(add_third_repository=True)
    self.assertEqual([], os.listdir(self.working_directory))
    test_node.purgeOldTestSuite(test_suite_data)
    self.assertEqual([], os.listdir(self.working_directory))
    os.mkdir(os.path.join(self.working_directory, 'foo'))
    self.assertEqual(['foo'], os.listdir(self.working_directory))
    test_node.purgeOldTestSuite(test_suite_data)
    self.assertEqual(['foo'], os.listdir(self.working_directory))
    os.mkdir(os.path.join(self.working_directory, 'bar'))
    self.assertEqual(set(['bar','foo']),
                      set(os.listdir(self.working_directory)))
    test_node.purgeOldTestSuite(test_suite_data)
    self.assertEqual(['foo'], os.listdir(self.working_directory))

  def test_purgeOldTestSuiteChmodNonWriteable(self):
    """Old test suites can be deleted even when some files/directories have
    been chmod'd to make non-writeable  """
    test_node = self.getTestNode()
    test_suite_data = self.getTestSuiteData(add_third_repository=True)
    os.mkdir(os.path.join(self.working_directory, 'bar'))
    non_writable_file = open(os.path.join(self.working_directory, 'bar', 'non-writable-file'), 'w')
    non_writable_file.close()

    os.chmod(os.path.join(self.working_directory, 'bar', 'non-writable-file'), 0o400) # -r--------
    os.chmod(os.path.join(self.working_directory, 'bar'), 0o500) # dr-x------

    test_node.purgeOldTestSuite(test_suite_data) # should not fail
    self.assertEqual([], os.listdir(self.working_directory))

  def test_purgeOldTestSuiteChmodNonWriteableNonReadable(self):
    """Old test suites can be deleted even when some files/directories have
    been chmod'd to make them non readable and non writeable. """
    test_node = self.getTestNode()
    test_suite_data = self.getTestSuiteData(add_third_repository=True)
    os.mkdir(os.path.join(self.working_directory, 'bar'))
    non_writable_file = open(os.path.join(self.working_directory, 'bar', 'non-writable-file'), 'w')
    non_writable_file.close()

    os.chmod(os.path.join(self.working_directory, 'bar', 'non-writable-file'), 0o000) # ----------
    os.chmod(os.path.join(self.working_directory, 'bar'), 0o000) # d---------

    test_node.purgeOldTestSuite(test_suite_data) # should not fail
    self.assertEqual([], os.listdir(self.working_directory))

  def test_09_runTestSuite(self, my_test_type='UnitTest'):
    """
    Check parameters passed to runTestSuite
    Also make sure that optional parameters are passed when needed
    """
    call_parameter_list = []
    parser = argparse.ArgumentParser()
    parser.add_argument('--foo', type=int)
    parser.add_argument('--hello_world', help='Hello world!')
    def spawn(*args, **kw):
      if args[1] == '--help':
        return {'stdout': parser.format_help()}
      call_parameter_list.append(args)

    test_node = self.getTestNode()
    test_node.process_manager.spawn = spawn
    runner = test_type_registry[my_test_type](test_node)
    # Create and initialise/regenerate a nodetestsuite
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    node_test_suite.revision_list = ('dummy', (0, '')),

    path = runner.getInstanceRoot(node_test_suite) + '/a/bin/runTestSuite'
    os.makedirs(os.path.dirname(path))
    os.close(os.open(path, os.O_CREAT))

    expected_parameter_list = [path,
      '--master_url', 'http://foo.bar',
      '--revision', 'dummy=0-',
      '--test_suite', 'Foo',
      '--test_suite_title', 'Foo-Test',
    ]
    def checkRunTestSuiteParameters():
      runner.runTestSuite(node_test_suite, "http://foo.bar")
      self.assertEqual(list(call_parameter_list.pop()), expected_parameter_list)
      self.assertFalse(call_parameter_list)

    checkRunTestSuiteParameters()

    def part(path): # in "bar" SR
      path = test_node.config['slapos_directory'] \
        + '/soft/37b51d194a7513e45b56f6524f2d51f2/parts/' + path
      os.makedirs(os.path.dirname(path))
      os.close(os.open(path, os.O_CREAT))
      return path
    for option in (
        ('--firefox_bin', part('firefox/firefox-slapos')),
        ('--frontend_url', 'http://frontend/'),
        ('--node_quantity', '3'),
        ('--xvfb_bin', part('xserver/bin/Xvfb')),
      ):
      parser.add_argument(option[0])
      expected_parameter_list += option
      checkRunTestSuiteParameters()

  def test_10_prepareSlapOS(self, my_test_type='UnitTest'):
    test_node = self.getTestNode()
    test_node_slapos = SlapOSInstance(self.slapos_directory)
    runner = test_type_registry[my_test_type](test_node)
    node_test_suite = test_node.getNodeTestSuite('foo')
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

    original_SlapOSControler_initializeSlapOSControler = SlapOSControler.initializeSlapOSControler
    original_SlapOSControler_runSoftwareRelease = SlapOSControler.runSoftwareRelease
    original_SlapOSControler_runComputerPartition = SlapOSControler.runComputerPartition
    try:
      SlapOSControler.initializeSlapOSControler = Patch("initializeSlapOSControler")
      SlapOSControler.runSoftwareRelease = Patch("runSoftwareRelease")
      SlapOSControler.runComputerPartition = Patch("runComputerPartition")
      method_list_for_prepareSlapOSForTestNode = ["initializeSlapOSControler",
                                                    "runSoftwareRelease"]
      method_list_for_prepareSlapOSForTestSuite = ["initializeSlapOSControler",
                                  "runSoftwareRelease", "runComputerPartition"]
      runner.prepareSlapOSForTestNode(test_node_slapos)
      self.assertEqual(method_list_for_prepareSlapOSForTestNode,
                        [x["method_name"] for x in call_list])
      call_list = []
      runner.prepareSlapOSForTestSuite(node_test_suite)
      self.assertEqual(method_list_for_prepareSlapOSForTestSuite,
                        [x["method_name"] for x in call_list])
      call_list = []
      SlapOSControler.runSoftwareRelease = Patch("runSoftwareRelease", status_code=1)
      # TODO : write a test for scalability case
      self.assertRaises(SubprocessError, runner.prepareSlapOSForTestSuite,
                      node_test_suite)
    finally:
      SlapOSControler.initializeSlapOSControler = original_SlapOSControler_initializeSlapOSControler
      SlapOSControler.runSoftwareRelease = original_SlapOSControler_runSoftwareRelease
      SlapOSControler.runComputerPartition = original_SlapOSControler_runComputerPartition

  def test_11_run(self, my_test_type='UnitTest', grade='master'):
    def doNothing(self, *args, **kw):
        pass
    # Used in case of 'ScalabilityTest'
    def patch_getTestType(self, *args, **kw):
      return my_test_type
    def patch_getSlaposAccountKey(self, *args, **kw):
      return "key"
    def patch_getSlaposAccountCertificate(self, *args, **kw):
      return "Certificate"
    def patch_getSlaposUrl(self, *args, **kw):
      return "http://Foo"
    def patch_getSlaposHateoasUrl(self, *args, **kw):
      return "http://Foo"
    def patch_generateConfiguration(self, *args, **kw):
      return json.dumps({"configuration_list": [{}], "involved_nodes_computer_guid"\
: [], "error_message": "No error.", "launcher_nodes_computer_guid": [], \
"launchable": False, "randomized_path" : "azertyuiop"})
    def patch_isMasterTestnode(self, *args, **kw):
      return (grade == 'master')
    test_self = self
    test_result_path_root = os.path.join(test_self._temp_dir,'test/results')
    os.makedirs(test_result_path_root)
    global counter
    counter = 0
    def patch_startTestSuite(self,node_title,computer_guid='unknown'):
      global counter
      config_list = []
      # Sclalability slave testnode is not directly in charge of testsuites
      if my_test_type == 'ScalabilityTest' and grade == 'slave':
        if counter == 5:
          raise StopIteration
        counter += 1
        return json.dumps([])

      def _checkExistingTestSuite(reference_set):
        test_self.assertEqual(set(reference_set),
                  set(os.listdir(test_node.working_directory)))
        for x in reference_set:
          test_self.assertTrue(os.path.exists(os.path.join(
                             test_node.working_directory,x)),True)
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
      if counter != 3 or project_title == 'qux':
        test_result_path = os.path.join(test_result_path_root, test_title)
        return TestResultProxy(self._proxy, self._retry_time,
                logger, test_result_path, node_title, revision)
    def patch_runTestSuite(self, *argv, **kw):
      return {'status_code':0}
    original_sleep = time.sleep
    time.sleep = doNothing
    self.generateTestRepositoryList()
    RunnerClass = test_type_registry[my_test_type]
    # Patch
    if my_test_type == "ScalabilityTest":
      original_getSlaposAccountKey = TaskDistributor.getSlaposAccountKey
      original_getSlaposAccountCertificate = TaskDistributor.getSlaposAccountCertificate
      original_getSlaposUrl = TaskDistributor.getSlaposUrl
      original_getSlaposHateoasUrl = TaskDistributor.getSlaposHateoasUrl
      original_isMasterTestnode = TaskDistributor.isMasterTestnode
      original_updateInstanceXML = RunnerClass._updateInstanceXML
      original_SlapOSMasterCommunicator__init__ = SlapOSMasterCommunicator.__init__
      TaskDistributor.getSlaposAccountKey = patch_getSlaposAccountKey
      TaskDistributor.getSlaposAccountCertificate = patch_getSlaposAccountCertificate
      TaskDistributor.getSlaposUrl = patch_getSlaposUrl
      TaskDistributor.getSlaposHateoasUrl = patch_getSlaposHateoasUrl
      TaskDistributor.isMasterTestnode = patch_isMasterTestnode
      RunnerClass._updateInstanceXML = doNothing
      SlapOSMasterCommunicator.__init__ = doNothing
    original_generateConfiguration = TaskDistributor.generateConfiguration
    original_initializeSlapOSControler = SlapOSControler.initializeSlapOSControler

    TaskDistributor.generateConfiguration = patch_generateConfiguration
    original_startTestSuite = TaskDistributor.startTestSuite
    original_subscribeNode = TaskDistributor.subscribeNode
    original_getTestType = TaskDistributor.getTestType
    original_createTestResult = TaskDistributor.createTestResult
    TaskDistributor.startTestSuite = patch_startTestSuite
    TaskDistributor.subscribeNode = doNothing
    TaskDistributor.getTestType = patch_getTestType
    TaskDistributor.createTestResult = patch_createTestResult

    # TestNode
    test_node = self.getTestNode()
    # Modify class UnitTestRunner(or more after) method
    def patch_prepareSlapOS(*args, **kw):
      return {'status_code':0}
    original_prepareSlapOS = RunnerClass._prepareSlapOS
    original_runTestSuite = RunnerClass.runTestSuite
    RunnerClass._prepareSlapOS = patch_prepareSlapOS
    RunnerClass.runTestSuite = patch_runTestSuite
    SlapOSControler.initializeSlapOSControler = doNothing
    # Inside test_node a runner is created using new UnitTestRunner methods
    test_node.run()
    self.assertEqual(5, counter)
    time.sleep = original_sleep
    # Restore old class methods
    if my_test_type == "ScalabilityTest":
      TaskDistributor.getSlaposAccountKey = original_getSlaposAccountKey
      TaskDistributor.getSlaposAccountCertificate = original_getSlaposAccountCertificate
      TaskDistributor.getSlaposUrl = original_getSlaposUrl
      TaskDistributor.getSlaposHateoasUrl = original_getSlaposHateoasUrl
      TaskDistributor.isMasterTestnode = original_isMasterTestnode
      RunnerClass._updateInstanceXML = original_updateInstanceXML
      SlapOSMasterCommunicator.__init__ = original_SlapOSMasterCommunicator__init__
    TaskDistributor.generateConfiguration = original_generateConfiguration
    TaskDistributor.startTestSuite = original_startTestSuite
    TaskDistributor.createTestResult = original_createTestResult
    TaskDistributor.subscribeNode = original_subscribeNode
    TaskDistributor.getTestType = original_getTestType
    RunnerClass._prepareSlapOS = original_prepareSlapOS
    RunnerClass.runTestSuite = original_runTestSuite
    SlapOSControler.initializeSlapOSControler = original_initializeSlapOSControler

  def test_12_spawn(self):
    def _checkCorrectStatus(expected_status,*args):
      result = process_manager.spawn(*args)
      self.assertEqual(result['status_code'], expected_status)
    process_manager = ProcessManager(max_timeout=1)
    _checkCorrectStatus(0, *['sleep','0'])
    # We must make sure that if the command is too long that
    # it will be automatically killed
    self.assertRaises(SubprocessError, process_manager.spawn, 'sleep','3')

  def test_13_SlaposControlerResetSoftware(self):
    test_node = self.getTestNode()
    controler = SlapOSControler(self.working_directory, test_node.config)
    os.mkdir(controler.software_root)
    file_name = 'AC_Ra\xc3\xadzertic\xc3\xa1ma'
    non_ascii_file = open(os.path.join(controler.software_root, file_name), 'w')
    non_ascii_file.close()
    self.assertEqual([file_name], os.listdir(controler.software_root))
    controler._resetSoftware()
    self.assertEqual([], os.listdir(controler.software_root))

  def test_14_createFolder(self):
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    folder = node_test_suite.test_suite_directory
    self.assertFalse(os.path.exists(folder))
    createFolder(folder)
    self.assertTrue(os.path.exists(folder))
    to_drop_path = os.path.join(folder, 'drop')
    to_drop = open(to_drop_path, 'w')
    to_drop.close()
    self.assertTrue(os.path.exists(to_drop_path))
    createFolder(folder, clean=True)
    self.assertFalse(os.path.exists(to_drop_path))

  def test_15_suite_log_directory(self, my_test_type='UnitTest', grade='master'):
    def doNothing(self, *args, **kw):
      pass
    # Used in case of 'ScalabilityTest'
    def patch_getTestType(self, *args, **kw):
      return my_test_type
    def patch_getSlaposAccountKey(self, *args, **kw):
      return "key"
    def patch_getSlaposAccountCertificate(self, *args, **kw):
      return "Certificate"
    def patch_getSlaposUrl(self, *args, **kw):
      return "http://Foo"
      return "Certificate"
    def patch_getSlaposHateoasUrl(self, *args, **kw):
      return "http://Foo"
    def patch_generateConfiguration(self, *args, **kw):
      return json.dumps({"configuration_list": [{}], "involved_nodes_computer_guid"\
: [], "error_message": "No error.", "launcher_nodes_computer_guid": [], \
"launchable": False, "randomized_path" : "azertyuiop"})
    def patch_isMasterTestnode(self, *args, **kw):
      return grade == 'master'
    test_self = self
    test_result_path_root = os.path.join(test_self._temp_dir,'test/results')
    os.makedirs(test_result_path_root)
    global counter
    counter = 0
    def patch_startTestSuite(self,node_title,computer_guid='unknown'):
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
      return TestResultProxy(self._proxy, self._retry_time,
                logger, test_result_path, node_title, revision)
    def patch_runTestSuite(self,*argv, **kw):
      return {'status_code':0}
    def checkTestSuite(test_node):
      test_node.node_test_suite_dict
      rand_part_set = set()
      self.assertEqual(2, len(test_node.node_test_suite_dict))
      for ref, suite in test_node.node_test_suite_dict.items():
        self.assertTrue('var/log/testnode/%s' % suite.reference in \
                         suite.suite_log_path,
                         "Incorrect suite log path : %r" % suite.suite_log_path)
        m = re.search('-(.*)/suite.log$', suite.suite_log_path)
        rand_part = m.groups()[0]
        self.assertEqual(len(rand_part), 10)
        self.assertNotIn(rand_part, rand_part_set)
        rand_part_set.add(rand_part)
        with open(suite.suite_log_path) as suite_log:
          self.assertIn("Getting configuration from test suite",
                        suite_log.readline())

    RunnerClass = test_type_registry[my_test_type]
    original_sleep = time.sleep
    time.sleep = doNothing
    self.generateTestRepositoryList()
    if my_test_type == "ScalabilityTest":
      original_getSlaposAccountKey = TaskDistributor.getSlaposAccountKey
      original_getSlaposAccountCertificate = TaskDistributor.getSlaposAccountCertificate
      original_getSlaposUrl = TaskDistributor.getSlaposUrl
      original_getSlaposHateoasUrl = TaskDistributor.getSlaposHateoasUrl
      original_isMasterTestnode = TaskDistributor.isMasterTestnode
      original_supply = SlapOSControler.supply
      original_request = SlapOSControler.request
      original_updateInstanceXML = RunnerClass._updateInstanceXML
      original_SlapOSMasterCommunicator__init__ = SlapOSMasterCommunicator.__init__
      TaskDistributor.getSlaposAccountKey = patch_getSlaposAccountKey
      TaskDistributor.getSlaposAccountCertificate = patch_getSlaposAccountCertificate
      TaskDistributor.getSlaposUrl = patch_getSlaposUrl
      TaskDistributor.getSlaposHateoasUrl = patch_getSlaposHateoasUrl
      TaskDistributor.isMasterTestnode = patch_isMasterTestnode
      SlapOSControler.supply = doNothing
      SlapOSControler.request = doNothing
      RunnerClass._updateInstanceXML = doNothing
      SlapOSMasterCommunicator.__init__ = doNothing
    original_generateConfiguration = TaskDistributor.generateConfiguration
    original_startTestSuite = TaskDistributor.startTestSuite
    original_subscribeNode = TaskDistributor.subscribeNode
    original_getTestType = TaskDistributor.getTestType
    TaskDistributor.generateConfiguration = patch_generateConfiguration
    TaskDistributor.startTestSuite = patch_startTestSuite
    TaskDistributor.subscribeNode = doNothing
    TaskDistributor.getTestType = patch_getTestType
    original_createTestResult = TaskDistributor.createTestResult
    TaskDistributor.createTestResult = patch_createTestResult
    test_node = self.getTestNode()
    del test_node.suiteLog
    # Change UnitTestRunner class methods
    original_prepareSlapOS = RunnerClass._prepareSlapOS
    original_runTestSuite = RunnerClass.runTestSuite
    original_initializeSlapOSControler = SlapOSControler.initializeSlapOSControler

    if my_test_type == "ScalabilityTest":
      RunnerClass.runTestSuite = patch_runTestSuite
    else:
      RunnerClass.runTestSuite = doNothing

    def patch_prepareSlapOS(*args, **kw):
      return {'status_code':0}
    RunnerClass._prepareSlapOS = patch_prepareSlapOS
    SlapOSControler.initializeSlapOSControler = doNothing
    test_node.run()
    self.assertEqual(counter, 3)
    checkTestSuite(test_node)
    time.sleep = original_sleep
    # Restore old class methods
    if my_test_type == "ScalabilityTest":
      TaskDistributor.getSlaposAccountKey = original_getSlaposAccountKey
      TaskDistributor.getSlaposAccountCertificate = original_getSlaposAccountCertificate
      TaskDistributor.getSlaposUrl = original_getSlaposUrl
      TaskDistributor.getSlaposHateoasUrl = original_getSlaposHateoasUrl
      TaskDistributor.isMasterTestnode = original_isMasterTestnode
      SlapOSControler.supply =original_supply
      SlapOSControler.request = original_request
      SlapOSControler.updateInstanceXML = original_updateInstanceXML
      SlapOSMasterCommunicator.__init__ = original_SlapOSMasterCommunicator__init__
    TaskDistributor.generateConfiguration = original_generateConfiguration
    TaskDistributor.startTestSuite = original_startTestSuite
    TaskDistributor.createTestResult = original_createTestResult
    TaskDistributor.subscribeNode = original_subscribeNode
    TaskDistributor.getTestType = original_getTestType
    RunnerClass._prepareSlapOS = original_prepareSlapOS
    RunnerClass.runTestSuite = original_runTestSuite
    SlapOSControler.initializeSlapOSControler = original_initializeSlapOSControler

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
    os.mkdir(os.path.join(temp_directory, 'something')) # this will be kept, as it's not a buildout tempfile
    os.mkdir(os.path.join(temp_directory, 'tmpC'))
    os.mkdir(os.path.join(temp_directory, 'tmp-cannot-delete'), 0o000)

    check(set(['buildoutA', 'something', 'tmpC', 'tmp-cannot-delete']))
    # default log file time is 15 days, so nothing is going to be deleted
    test_node._cleanupTemporaryFiles()
    check(set(['buildoutA', 'something', 'tmpC', 'tmp-cannot-delete']))
    # then we set keep time to 0, folder will be deleted
    test_node.max_temp_time = 0
    test_node._cleanupTemporaryFiles()
    # "something" is kept, as it is not a buildout related tmpfile
    check(set(['something']))
    # other buildout related files are all deleted now.
    self.assertEqual(
        set([]) ,
        set(['buildoutA', 'tmpC', 'tmp-cannot-delete']).intersection(
            set(os.listdir(temp_directory))))

  def test_18_resetSoftwareAfterManyBuildFailures(self, my_test_type='UnitTest'):
    """
    Check that after several building failures that the software is resetted
    """
    initial_initializeSlapOSControler = \
      SlapOSControler.initializeSlapOSControler
    initial_runSoftwareRelease = SlapOSControler.runSoftwareRelease
    test_node = self.getTestNode()
    runner = test_type_registry[my_test_type](test_node)
    node_test_suite = test_node.getNodeTestSuite('foo')
    init_call_kw_list = []
    def initializeSlapOSControler(self, **kw):
      init_call_kw_list.append(kw)
    def runSoftwareRelease(self, *args, **kw):
      return {"status_code": 1}
    SlapOSControler.initializeSlapOSControler = initializeSlapOSControler
    SlapOSControler.runSoftwareRelease = runSoftwareRelease
    def callPrepareSlapOS():
      runner._prepareSlapOS(self.working_directory, node_test_suite,
         create_partition=0)
    def callRaisingPrepareSlapos():
      self.assertRaises(SubprocessError, callPrepareSlapOS)

    self.assertEqual(node_test_suite.retry_software_count, 0)
    for x in range(11):
      callRaisingPrepareSlapos()
    self.assertEqual(len(init_call_kw_list), 11)
    self.assertEqual(init_call_kw_list[-1]['reset_software'], False)
    self.assertEqual(node_test_suite.retry_software_count, 11)
    callRaisingPrepareSlapos()
    self.assertEqual(init_call_kw_list[-1]['reset_software'], True)
    self.assertEqual(node_test_suite.retry_software_count, 1)
    callRaisingPrepareSlapos()
    self.assertEqual(init_call_kw_list[-1]['reset_software'], False)
    self.assertEqual(node_test_suite.retry_software_count, 2)
    SlapOSControler.initializeSlapOSControler = \
      initial_initializeSlapOSControler
    SlapOSControler.runSoftwareRelease = initial_runSoftwareRelease

  def test_scalability_04_constructProfile(self, my_test_type='ScalabilityTest'):
    self.test_04_constructProfile(my_test_type)
  def test_scalability_05b_changeRepositoryBranch(self, my_test_type='ScalabilityTest'):
    self.test_05b_changeRepositoryBranch(my_test_type)
  def test_scalability_09_runTestSuite(self, my_test_type='ScalabilityTest'):
    # TODO : write own scalability test
    pass
  def test_scalability_10_prepareSlapOS(self, my_test_type='ScalabilityTest'):
    # TODO : write own scalability test
    # This case test may be dispensable on ScalabilityTest case
    # so..
    pass
  @unittest.skip("Not implemented")
  def test_scalability_as_master_11_run(self, my_test_type='ScalabilityTest'):
    self.test_11_run(my_test_type, grade='master')
  # TODO : add a test with master and a launchable testsuite -> patch a lot of methods
  @unittest.skip("Not implemented")
  def test_scalability_as_slave_11_run(self, my_test_type='ScalabilityTest'):
    self.test_11_run(my_test_type, grade='slave')
  @unittest.skip("Not implemented")
  def test_scalability_as_master_15_suite_log_directory(self, my_test_type='ScalabilityTest'):
    self.test_15_suite_log_directory(my_test_type, grade='master')
  @unittest.skip("Not implemented")
  def test_scalability_as_slave_15_suite_log_directory(self, my_test_type='ScalabilityTest'):
    self.test_15_suite_log_directory(my_test_type, grade='slave')
  def test_scalability_18_resetSoftwareAfterManyBuildFailures(self, my_test_type='ScalabilityTest'):
    # TODO : write own scalability test
    pass

  def test_zzzz_scalability_19_xxxx(self):
    # TODO : fill the dummy slapos answer
    # by patching isSoftwareReleaseReady method.
    def patch_createTestResult(self, revision, test_name_list, node_title,
            allow_restart=False, test_title=None, project_title=None):
      test_result_path = os.path.join(test_result_path_root, test_title)
      return TestResultProxy(self._proxy, self._retry_time,
                logger, test_result_path, node_title, revision)
    global startTestSuiteDone
    startTestSuiteDone = False
    def patch_startTestSuite(self,node_title,computer_guid='unknown'):
      config_list = []
      global startTestSuiteDone
      if not startTestSuiteDone:
        startTestSuiteDone = True
        config_list.append(test_self.getTestSuiteData(reference='foo')[0])
        config_list.append(test_self.getTestSuiteData(reference='bar')[0])
      else:
        raise StopIteration
      return json.dumps(config_list)
    def patch_isMasterTestnode(self, *args, **kw):
      return True
    def patch_generateConfiguration(self, *args, **kw):
      return json.dumps({"configuration_list": [{"ok":"ok"}], "involved_nodes_computer_guid"\
: ["COMP1", "COMP2", "COMP3"], "error_message": "No error.", "launcher_nodes_computer_guid": ["COMP1"], \
"launchable": True, "randomized_path" : "azertyuiop"})
    def doNothing(self, *args, **kw):
        pass
    def patch_getSlaposAccountKey(self, *args, **kw):
      return "key"
    def patch_getSlaposAccountCertificate(self, *args, **kw):
      return "Certificate"
    def patch_getSlaposUrl(self, *args, **kw):
      return "http://Foo"
    def patch_getSlaposHateoasUrl(self, *args, **kw):
      return "http://Foo"
    def patch_getTestType(self, *args, **kw):
      return "ScalabilityTest"
    def patch_runTestSuite(self, *args, **kw):
      return {'status_code':0}
    def patch_generateProfilePasswordAccess(self, *args, **kw):
      return "user", "pass"
    def patch_getDictionaryFromFile(self, *args, **kw):
      return []
    test_self = self
    test_result_path_root = os.path.join(test_self._temp_dir,'test/results')
    os.makedirs(test_result_path_root)
    self.generateTestRepositoryList()
    # Select the good runner to modify
    RunnerClass = test_type_registry['ScalabilityTest']
    # Patch methods
    original_sleep = time.sleep
    original_getSlaposAccountKey = TaskDistributor.getSlaposAccountKey
    original_getSlaposAccountCertificate = TaskDistributor.getSlaposAccountCertificate
    original_getSlaposUrl = TaskDistributor.getSlaposUrl
    original_getSlaposHateoasUrl = TaskDistributor.getSlaposHateoasUrl
    original_generateConfiguration = TaskDistributor.generateConfiguration
    original_isMasterTestnode = TaskDistributor.isMasterTestnode
    original_startTestSuite = TaskDistributor.startTestSuite
    original_subscribeNode = TaskDistributor.subscribeNode
    original_getTestType = TaskDistributor.getTestType
    original_createTestResult = TaskDistributor.createTestResult
    original_prepareSlapOS = RunnerClass._prepareSlapOS
    original_runTestSuite = RunnerClass.runTestSuite
    original_supply = SlapOSControler.supply
    original_request = SlapOSControler.request
    original_updateInstanceXML = SlapOSControler.updateInstanceXML
    original_SlapOSMasterCommunicator__init__ = SlapOSMasterCommunicator.__init__
    original_generateProfilePasswordAccess = RunnerClass.generateProfilePasswordAccess
    original_getDictionaryFromFile = RunnerClass.getDictionaryFromFile
    original_updateDictionaryFile = RunnerClass.updateDictionaryFile
    original__createInstance = RunnerClass._createInstance
    original__waitInstanceCreation = RunnerClass._waitInstanceCreation

    time.sleep = doNothing
    TaskDistributor.getSlaposAccountKey = patch_getSlaposAccountKey
    TaskDistributor.getSlaposAccountCertificate = patch_getSlaposAccountCertificate
    TaskDistributor.getSlaposUrl = patch_getSlaposUrl
    TaskDistributor.getSlaposHateoasUrl = patch_getSlaposHateoasUrl
    TaskDistributor.generateConfiguration = patch_generateConfiguration
    TaskDistributor.isMasterTestnode = patch_isMasterTestnode
    TaskDistributor.startTestSuite = patch_startTestSuite
    TaskDistributor.subscribeNode = doNothing
    TaskDistributor.getTestType = patch_getTestType
    TaskDistributor.createTestResult = patch_createTestResult
    RunnerClass._prepareSlapOS = doNothing
    RunnerClass.runTestSuite = patch_runTestSuite
    SlapOSControler.supply = doNothing
    SlapOSControler.request = doNothing
    SlapOSControler.updateInstanceXML = doNothing
    SlapOSMasterCommunicator.__init__ = doNothing
    RunnerClass.generateProfilePasswordAccess = patch_generateProfilePasswordAccess
    RunnerClass.updateDictionaryFile = doNothing
    RunnerClass.getDictionaryFromFile = patch_getDictionaryFromFile
    RunnerClass._createInstance = doNothing
    RunnerClass._waitInstanceCreation = doNothing
    # Run
    test_node = self.getTestNode()
    test_node.run()
    # Restore methods
    TaskDistributor.getSlaposAccountKey = original_getSlaposAccountKey
    TaskDistributor.getSlaposAccountCertificate = original_getSlaposAccountCertificate
    TaskDistributor.getSlaposUrl = original_getSlaposUrl
    TaskDistributor.getSlaposHateoasUrl = original_getSlaposHateoasUrl
    TaskDistributor.generateConfiguration = original_generateConfiguration
    TaskDistributor.isMasterTestnode = original_isMasterTestnode
    TaskDistributor.startTestSuite = original_startTestSuite
    TaskDistributor.createTestResult = original_createTestResult
    TaskDistributor.subscribeNode = original_subscribeNode
    TaskDistributor.getTestType = original_getTestType
    RunnerClass._prepareSlapOS = original_prepareSlapOS
    RunnerClass.runTestSuite = original_runTestSuite
    SlapOSControler.supply = original_supply
    SlapOSControler.request = original_request
    SlapOSControler.updateInstanceXML = original_updateInstanceXML
    SlapOSMasterCommunicator.__init__ = original_SlapOSMasterCommunicator__init__
    time.sleep =original_sleep
    RunnerClass.generateProfilePasswordAccess = original_generateProfilePasswordAccess
    RunnerClass.getDictionaryFromFile = original_getDictionaryFromFile
    RunnerClass.updateDictionaryFile = original_updateDictionaryFile
    RunnerClass._createInstance = original__createInstance
    RunnerClass._waitInstanceCreation = original__waitInstanceCreation
