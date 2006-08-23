#
# ERP5 Folder unit test suite.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

#from random import randint
from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG, INFO
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.ERP5Type import ERP5TypeInformation

class TestFolder(ERP5TypeTestCase, LogInterceptor):

    # Some helper methods

    def getTitle(self):
      return "Folder"

    def getBusinessTemplateList(self):
      """
        Return the list of business templates.
      """
      return tuple()

    def afterSetUp(self):
      """
        Executed before each test_*.
      """
      self.login()
      self.folder = self.getPortal().newContent(id='TestFolder', portal_type='Folder')

    def beforeTearDown(self):
      """
        Executed after each test_*.
      """
      self.getPortal().manage_delObjects(ids=[self.folder.getId()])

    def newContent(self):
      """
        Create an object in self.folder and return it.
      """
      return self.folder.newContent(portal_type='Folder')
    
    def test_01_folderType(self, quiet=0, run=1):
      """
        Test if the present Folder class is the ERP5 version of Folder, not CMF's.
      """
      if not run : return
      if not quiet:
        message = 'Test folderType value'
        LOG('Testing... ', 0, message)
      self.assertTrue(isinstance(self.getTypesTool()['Folder'], ERP5TypeInformation))

    def test_02_defaultGenerateNewId(self, quiet=0, run=1):
      """
        Test the default Id generation method.
        Ids are incremented at content creation and start at 1.
      """
      if not run : return
      if not quiet:
        message = 'Test default generateNewId'
        LOG('Testing... ', 0, message)
      self.assertEquals(self.folder.getIdGenerator(), '') # No id generator defined
      #assertEqual(self.folder.getIdGroup(), None) # Folder belongs to no group (this would trigger use of portalIds).
      self.assertEquals(len(self.folder), 0)
      object = self.newContent()
      self.assertEquals(object.getId(), '1')
      object = self.newContent()
      self.assertEquals(object.getId(), '2')
    
    def test_03_customGenerateNewId(self, quiet=0, run=1):
      """
        Test that id_generator property is honored.
      """
      if not run : return
      if not quiet:
        message = 'Test custom generateNewId'
        LOG('Testing... ', 0, message)
      id_generator_script_name = 'testIdGenerator'
      id_generator_id_list = ['first_id', 'second_id']
      createZODBPythonScript(self.getPortal().portal_skins.erp5_core,
                             id_generator_script_name, '', 'return %s[len(context)]' % (repr(id_generator_id_list), ))
      self.folder.setIdGenerator(id_generator_script_name)
      self.assertEquals(self.folder.getIdGenerator(), id_generator_script_name)
      for expected_length in xrange(len(id_generator_id_list)):
        self.assertEquals(len(self.folder), expected_length)
        object = self.newContent()
        self.assertEquals(object.getId(), id_generator_id_list[expected_length])
    
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestFolder))
        return suite
