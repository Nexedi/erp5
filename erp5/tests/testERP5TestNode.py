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
import os
import shutil
import subprocess
import tempfile

class ERP5TestNode(TestCase):

  def setUp(self):
    self._tempdir = tempfile.mkdtemp()
    self.working_directory = os.path.join(self._tempdir, 'testnode')
    self.slapos_directory = os.path.join(self._tempdir, 'slapos')
    self.remote_repository0 = os.path.join(self._tempdir, 'rep0')
    self.remote_repository1 = os.path.join(self._tempdir, 'rep1')
    os.mkdir(self.working_directory)
    os.mkdir(self.slapos_directory)
    os.mkdir(self.remote_repository0)
    os.mkdir(self.remote_repository1)

  def tearDown(self):
    shutil.rmtree(self._tempdir, True)

  def getTestNode(self):
    def log(*args):
      for arg in args:
        print "TESTNODE LOG : %r" % (arg,)
    # XXX how to get property the git path ?
    config = {"git_binary": "/srv/slapgrid/slappart80/srv/runner/software/ba1e09f3364989dc92da955b64e72f8d/parts/git/bin/git"}
    return TestNode(log, config)

  def updateNodeTestSuiteData(self, node_test_suite):
    node_test_suite.edit(working_directory=self.working_directory,
        test_suite="Foo",
        project_title="Foo",
        test_suite_title="Foo-Test",
        vcs_repository_list=[
            {'url': self.remote_repository0,
             'profile_path': 'software.cfg',
             'branch': 'master'},
            {'url': self.remote_repository1,
             'buildout_section_id': 'rep1',
             'branch': 'master'}])

  def getCaller(self, **kw):
    class Caller(object):

      def __init__(self, **kw):
        self.__dict__.update(**kw)

      def __call__(self, command):
        return subprocess.check_output(command, **self.__dict__)
    return Caller(**kw)

  def generateTestRepositoryList(self):
    last_commit_list = []
    for i, repository_path in enumerate([self.remote_repository0,
                                        self.remote_repository1]):
      call = self.getCaller(cwd=repository_path)
      call("git init".split())
      call("touch first_file".split())
      call("git add first_file".split())
      call("git commit -v -m first_commit".split() + ['--author="a b <a@b.c>"'])
      my_file = open(os.path.join(repository_path, 'first_file'), 'w')
      my_file.write("initial_content%i" % i)
      my_file.close()
      call("git commit -av -m next_commit".split() + ['--author="a b <a@b.c>"'])
      output = call("git log --oneline".split())
      output_line_list = output.split("\n")
      self.assertEquals(3, len(output_line_list))
      # remove additional return line
      output_line_list = output_line_list[0:2]
      expected_commit_list = ["next_commit", "first_commit"]
      last_commit_list.append(output_line_list[0].split())
      commit_list = [x.split()[1] for x in output_line_list]
      self.assertEquals(expected_commit_list, commit_list)
    # looks like [('d3d09e6', 'next_commit'), ('c4c15e0', 'next_commit')]
    # for respectively rep0 and rep1
    return last_commit_list

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

  def test_03_constructProfile(self):
    """
    Check if the software profile is correctly generated
    """
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    test_node.constructProfile(node_test_suite)
    self.assertEquals("%s/software.cfg" % (node_test_suite.working_directory,),
                      node_test_suite.custom_profile_path)
    profile = open(node_test_suite.custom_profile_path, 'r')
    expected_profile = """
[buildout]
extends = %s/testnode/foo/rep0/software.cfg

[rep1]
repository = %s/testnode/foo/rep1
branch = master
""" % (self._tempdir, self._tempdir)
    self.assertEquals(expected_profile, profile.read())
    profile.close()

  def test_04_getAndUpdateFullRevisionList(self):
    """
    Check if we clone correctly repositories and git right revisions
    """
    commit_list = self.generateTestRepositoryList()
    test_node = self.getTestNode()
    node_test_suite = test_node.getNodeTestSuite('foo')
    self.updateNodeTestSuiteData(node_test_suite)
    result = test_node.getAndUpdateFullRevisionList(node_test_suite)
    self.assertEquals(2, len(result))
    self.assertTrue(result[0].startswith('rep0=2-%s' % commit_list[0][0]))
    self.assertTrue(result[1].startswith('rep1=2-%s' % commit_list[1][0]))
