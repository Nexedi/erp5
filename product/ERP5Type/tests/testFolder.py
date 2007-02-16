#
# ERP5 Folder unit test suite.
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.CMFCore.tests.base.testcase import LogInterceptor
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.Cache import clearCache

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
      self.folder = self.getPortal().newContent(id='TestFolder',
                                                portal_type='Folder')
      self.other_folder = self.getPortal().newContent(
                    id='OtherTestFolder', portal_type='Folder')

    def beforeTearDown(self):
      """
        Executed after each test_*.
      """
      self.getPortal().manage_delObjects(ids=[self.folder.getId(),
                                          self.other_folder.getId()])
      clearCache()

    def newContent(self):
      """
        Create an object in self.folder and return it.
      """
      return self.folder.newContent(portal_type='Folder')
    
    def test_01_folderType(self, quiet=0, run=1):
      """
        Test if the present Folder class is the ERP5 version of Folder, not
        CMF's.
      """
      if not run : return
      if not quiet:
        message = 'Test folderType value'
        LOG('Testing... ', 0, message)
      self.assertTrue(isinstance(self.getTypesTool()['Folder'],
                      ERP5TypeInformation))

    def test_02_defaultGenerateNewId(self, quiet=0, run=1):
      """
        Test the default Id generation method.
        Ids are incremented at content creation and start at 1.
      """
      if not run : return
      if not quiet:
        message = 'Test default generateNewId'
        LOG('Testing... ', 0, message)
      # No id generator defined
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      obj = self.newContent()
      self.assertEquals(obj.getId(), '1')
      obj = self.newContent()
      self.assertEquals(obj.getId(), '2')
    
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
               id_generator_script_name, '',
               'return %s[len(context)]' % (repr(id_generator_id_list), ))
      self.folder.setIdGenerator(id_generator_script_name)
      self.assertEquals(self.folder.getIdGenerator(), id_generator_script_name)
      for expected_length in xrange(len(id_generator_id_list)):
        self.assertEquals(len(self.folder), expected_length)
        obj = self.newContent()
        self.assertEquals(obj.getId(), id_generator_id_list[expected_length])
 
    def _setAllowedContentTypesForFolderType(self, allowed_content_types):
      """Set allowed content types for Folder portal type."""
      folder_ti = self.getTypesTool()['Folder']
      folder_ti.allowed_content_types = allowed_content_types
      folder_ti.filter_content_types = True
    
    def _assertAllowedContentTypes(self, obj, expected_allowed_content_types):
      """Asserts that allowed content types for obj are exactly what we
      have in expected_allowed_content_types."""
      allowed_content_types_id_list = [x.getId() for
                                       x in obj.allowedContentTypes()]
      self.assertEquals(len(expected_allowed_content_types),
                        len(allowed_content_types_id_list),
                       'expected %s and actual %s have different length' % (
                        expected_allowed_content_types,
                        allowed_content_types_id_list
                       ))
      for portal_type_name in expected_allowed_content_types:
        self.failUnless(portal_type_name in allowed_content_types_id_list)

    def test_AllowedContentTypes(self):
      type_list = ['Folder', 'Category', 'Base Category']
      self._setAllowedContentTypesForFolderType(type_list)
      self._assertAllowedContentTypes(self.folder, type_list)

    def test_AllowedContentTypesCacheExpiration(self):
      type_list = ['Folder', 'Category', 'Base Category']
      self._setAllowedContentTypesForFolderType(type_list)
      self.folder.manage_permission(
                    'Add portal content', roles=[], acquire=0)
      self._assertAllowedContentTypes(self.folder, [])
      self.folder.manage_permission(
                    'Add portal content', roles=['Manager'], acquire=0)
      self._assertAllowedContentTypes(self.folder, type_list)

    def test_AllowedContentTypesObjectIndependance(self):
      type_list = ['Folder', 'Category', 'Base Category']
      self._setAllowedContentTypesForFolderType(type_list)
      self._assertAllowedContentTypes(self.folder, type_list)
      self.other_folder.manage_permission(
                    'Add portal content', roles=[], acquire=0)
      self._assertAllowedContentTypes(self.other_folder, [])
      self._assertAllowedContentTypes(self.folder, type_list)
    
    def test_NewContentAndAllowedContentTypes(self):
      self._setAllowedContentTypesForFolderType(('Folder', ))
      self.assertRaises(ValueError, self.folder.newContent,
                        portal_type='Category')

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestFolder))
        return suite
