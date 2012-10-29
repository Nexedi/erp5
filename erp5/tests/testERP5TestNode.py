from unittest import TestCase

import sys
sys.path[0:0] = [
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
    ]

from erp5.util.testnode import TestNode
import tempfile
import shutil
import os

class ERP5TestNode(TestCase):

  def setUp(self):
    self._tempdir = tempfile.mkdtemp()
    self.software_root = os.path.join(self._tempdir, 'software')
    self.instance_root = os.path.join(self._tempdir, 'instance')

  def tearDown(self):
    shutil.rmtree(self._tempdir, True)

  def getTestNode(self):
    return TestNode(None, None)

  def test_01_GetDelNodeTestSuite(self):
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
    node_test_suite.edit(working_directory="some_path")
    self.assertEquals("some_path/foo", node_test_suite.working_directory)

  def test_03_constructProfile(self):
    pass
