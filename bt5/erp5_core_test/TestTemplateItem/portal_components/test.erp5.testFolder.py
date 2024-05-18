##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Yoshinori Okuji <yo@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
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

import unittest

from BTrees.Length import Length
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import LogInterceptor
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5Type.ERP5Type import ERP5TypeInformation
from Products.ERP5Type.Cache import clearCache
from Products.ERP5Type.Core.Folder import FragmentedLength, FRAGMENTED_LENGTH_THRESHOLD
from AccessControl.ZopeGuards import guarded_getattr
from zExceptions import Unauthorized
from six.moves import range

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
    self.folder = self.portal.newContent(id='TestFolder',
                                              portal_type='Folder')
    self.other_folder = self.portal.newContent(
                  id='OtherTestFolder', portal_type='Folder')

  def beforeTearDown(self):
    """
      Executed after each test_*.
    """
    self.portal.manage_delObjects(ids=[self.folder.getId(),
                                        self.other_folder.getId()])
    clearCache()
    self.commit()

  def newContent(self):
    """
      Create an object in self.folder and return it.
    """
    return self.folder.newContent(portal_type='Folder')

  def test_01_folderType(self):
    """
      Test if the present Folder class is the ERP5 version of Folder, not
      CMF's.
    """
    self.assertTrue(isinstance(self.getTypesTool()['Folder'],
                    ERP5TypeInformation))

  def test_02_defaultGenerateNewId(self):
    """
      Test the default Id generation method.
      Ids are incremented at content creation and start at 1.
    """
    # No id generator defined
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj = self.newContent()
    self.assertEqual(obj.getId(), '1')
    obj = self.newContent()
    self.assertEqual(obj.getId(), '2')

  def test_03_customGenerateNewId(self):
    """
      Test that id_generator property is honored.
    """
    id_generator_script_name = 'testIdGenerator'
    id_generator_id_list = ['first_id', 'second_id']
    createZODBPythonScript(self.portal.portal_skins.erp5_core,
              id_generator_script_name, '',
              'return %s[len(context)]' % (repr(id_generator_id_list), ))
    self.folder.setIdGenerator(id_generator_script_name)
    self.assertEqual(self.folder.getIdGenerator(), id_generator_script_name)
    for expected_length in range(len(id_generator_id_list)):
      self.assertEqual(len(self.folder), expected_length)
      obj = self.newContent()
      self.assertEqual(obj.getId(), id_generator_id_list[expected_length])

  def test_03_unkownGenerateNewId(self):
    self.folder.setIdGenerator('no such method')
    self.assertRaises(ValueError, self.folder.generateNewId)
    self.assertRaises(ValueError, self.folder.newContent)

  def _setAllowedContentTypesForFolderType(self, allowed_content_type_list):
    """Set allowed content types for Folder portal type."""
    self.getTypesTool().Folder.edit(
      type_allowed_content_type_list=allowed_content_type_list,
      type_filter_content_type=True)

  def _assertAllowedContentTypes(self, obj, expected_allowed_content_types):
    """Asserts that allowed content types for obj are exactly what we
    have in expected_allowed_content_types."""
    self.assertEqual(sorted(expected_allowed_content_types),
                      sorted(x.getId() for x in obj.allowedContentTypes()))

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

  def test_editWithoutModifyPortalContent(self):
    _ = guarded_getattr(self.folder, 'edit')
    original_permission_list = self.folder.permission_settings('Modify portal content')
    assert len(original_permission_list) == 1
    self.folder.manage_permission('Modify portal content', [], 0)
    self.assertRaises(Unauthorized, guarded_getattr, self.folder, 'edit')
    # Reset to original permissions
    self.folder.manage_permission('Modify portal content', original_permission_list[0]['roles'], original_permission_list[0]['acquire'])

  def _createUpgradeObjectClassPythonScript(self):
    """Create a simple python script """
    createZODBPythonScript(self.portal.portal_skins.custom,
                    "test_upgradeObject", 'x',
                    'return [1]')
    return self.portal.portal_skins.custom.test_upgradeObject


  def test_upgradeObjectClass(self):
    """ Test if it changes Object Class """
    type_list = ['Folder', 'Category' ]
    self._setAllowedContentTypesForFolderType(type_list)
    obj = self.folder.newContent(portal_type="Category")
    from_class = obj.__class__
    to_class = self.folder.__class__
    test_script = self._createUpgradeObjectClassPythonScript()
    result = self.folder.upgradeObjectClass(test_script, from_class,
                                            to_class, test_script)
    self.commit()
    self.assertEqual(self.folder[obj.getId()].__class__, to_class)
    self.assertNotEqual(self.folder[obj.getId()].__class__, from_class)
    self.assertEqual([1], result)

  def test_upgradeObjectClassOnlyTest(self):
    """ Test if it DOES NOT change Object Class, only test it. """
    type_list = ['Folder', 'Category' ]
    self._setAllowedContentTypesForFolderType(type_list)
    obj = self.folder.newContent(portal_type="Category")
    from_class = obj.__class__
    to_class = self.folder.__class__
    test_script = self._createUpgradeObjectClassPythonScript()
    result = self.folder.upgradeObjectClass(test_script, from_class,
                                      to_class, test_script, test_only=1)
    self.commit()
    self.assertNotEqual(self.folder[obj.getId()].__class__, to_class)
    self.assertEqual(self.folder[obj.getId()].__class__, from_class)
    self.assertEqual([1], result)

  def test_upgradeObjectClassHierarchicaly(self):
    """ Test if migrate sub objects Hierarchicaly """
    type_list = ['Folder', 'Category', 'Base Category']
    self._setAllowedContentTypesForFolderType(type_list)
    subfolder = self.newContent()
    obj = subfolder.newContent(portal_type="Category")
    from_class = obj.__class__
    to_class = self.folder.__class__
    test_script = self._createUpgradeObjectClassPythonScript()
    result = self.folder.upgradeObjectClass(test_script, from_class,
                                            to_class, test_script)
    self.commit()
    self.assertEqual(subfolder[obj.getId()].__class__, to_class)
    self.assertNotEqual(subfolder[obj.getId()].__class__, from_class)
    self.assertEqual([1], result)

  def test_upgradeObjectClassWithSubObject(self):
    """ Test If upgrade preseve subobjects """
    type_list = ['Folder', 'Category', 'Base Category']
    self._setAllowedContentTypesForFolderType(type_list)
    subobject = self.folder.newContent(portal_type="Category")
    obj = subobject.newContent(portal_type="Category")
    from_class = obj.__class__
    to_class = self.folder.__class__
    test_script = self._createUpgradeObjectClassPythonScript()
    result = self.folder.upgradeObjectClass(test_script, from_class,
                                            to_class, test_script)
    self.commit()
    self.assertEqual(self.folder[subobject.getId()].__class__, to_class)
    self.assertNotEqual(self.folder[subobject.getId()].__class__, from_class)
    self.assertEqual(self.folder[subobject.getId()][obj.getId()].__class__, to_class)
    self.assertNotEqual(self.folder[subobject.getId()][obj.getId()].__class__, from_class)
    self.assertEqual([1, 1], result)

  def test_upgradeObjectClassWithStrings(self):
    """ Test if it changes Object Class """
    type_list = ['Folder', 'Category' ]
    self._setAllowedContentTypesForFolderType(type_list)
    obj = self.folder.newContent(portal_type="Category")
    from_class_as_string = 'erp5.portal_type.Category'
    to_class_as_string = 'erp5.portal_type.Folder'
    from_class = obj.__class__
    to_class = self.folder.__class__
    test_script = self._createUpgradeObjectClassPythonScript()
    result = self.folder.upgradeObjectClass(test_script, from_class_as_string,
                                            to_class_as_string, test_script)
    self.commit()
    self.assertEqual(self.folder[obj.getId()].__class__, to_class)
    self.assertNotEqual(self.folder[obj.getId()].__class__, from_class)
    self.assertEqual([1], result)

  def test_FolderMixinSecurity(self):
    """ Test if FolderMix methods cannot be called by URL """
    type_list = ['Folder']
    self._setAllowedContentTypesForFolderType(type_list)
    obj = self.folder.newContent(portal_type='Folder')
    self.commit()
    response = self.publish('%s/deleteContent?id=%s' % (
            self.folder.absolute_url(relative=True), obj.getId()))
    self.assertIn(obj.getId(), self.folder.objectIds())
    self.assertEqual(302, response.getStatus())

  def test_fragmentedLength(self):
    """Test Folder._count type and behaviour"""
    type_list = ['Folder']
    self._setAllowedContentTypesForFolderType(type_list)
    folder = self.folder
    folder_dict = folder.__dict__
    folder.newContent(portal_type='Folder')
    self.assertEqual(len(folder), 1)
    self.assertIsInstance(folder_dict['_count'], Length)
    original_length_oid = folder_dict['_count']._p_oid
    for _ in range(FRAGMENTED_LENGTH_THRESHOLD - len(folder) - 1):
      folder.newContent(portal_type='Folder')
    self.assertEqual(len(folder), FRAGMENTED_LENGTH_THRESHOLD - 1)
    self.assertIsInstance(folder_dict['_count'], Length)
    # Generate 3 to completely clear the threshold, as we do not care whether
    # the change happens when reaching the threshold or when going over it.
    folder.newContent(portal_type='Folder')
    folder.newContent(portal_type='Folder')
    folder.newContent(portal_type='Folder')
    self.assertEqual(len(folder), FRAGMENTED_LENGTH_THRESHOLD + 2)
    fragmented_length = folder_dict['_count']
    self.assertIsInstance(fragmented_length, FragmentedLength)
    self.assertEqual(len(fragmented_length._map), 2, fragmented_length._map)
    original_length = fragmented_length._map[None]
    self.assertEqual(original_length_oid, original_length._p_oid)
    self.assertGreater(original_length(), FRAGMENTED_LENGTH_THRESHOLD - 1)
    self.assertGreater(len(folder), original_length())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFolder))
  return suite
