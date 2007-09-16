##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                     Vincent Pelletier <vincent@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager

TESTED_SKIN_FOLDER_ID = 'custom'

class TestCachedSkinsTool(ERP5TypeTestCase):
  """
    Test Cached version of the CMF SkinsTool.
  """

  def getBusinessTemplateList(self):
    return tuple()

  def getTitle(self):
    return "CachedSkinsTool"

  def afterSetUp(self):
    self.login()
    skins_tool = self.getSkinsTool()
    tested_skin_folder = getattr(skins_tool, TESTED_SKIN_FOLDER_ID, None)
    if tested_skin_folder is None:
      skins_tool.manage_addProduct['OFSP'].manage_addFolder(id=TESTED_SKIN_FOLDER_ID)
    # Call changeSkin before each step to make sure SKINDATA is cleared
    # (request-scope cache).
    # Use None as skinname to keep using the default one.
    self.getSkinnableObject().changeSkin(skinname=None)

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('vincent', '', ['Manager'], [])
    user = uf.getUserById('vincent').__of__(uf)
    newSecurityManager(None, user)

  def getSkinnableObject(self):
    """
      Return the skinnable object (access to SkinsTool through cache).
    """
    return self.getPortal()
 
  def getSkinsTool(self):
    """
      Return the SkinsTool (access to SkinsSool without cache).
    """
    return self.getPortal().portal_skins

  def getTestedSkinFolder(self):
    """
      Return the Folder object in which the test should create its objects.
    """
    return self.getSkinsTool()[TESTED_SKIN_FOLDER_ID]

  def test_01_notExistingIsNotFound(self):
    """
      Check that the received class has the minimum requirements which makes
      a dict usable from zope restricted environment.
    """
    searched_object_id = 'dummyNotFound'
    self.assertTrue(getattr(self.getSkinnableObject(),  searched_object_id, None) is None)
    self.assertTrue(getattr(self.getTestedSkinFolder(), searched_object_id, None) is None)

  def test_02_createdIsFound(self):
    searched_object_id = 'dummyFound'
    tested_skin_folder = self.getTestedSkinFolder()
    tested_skin_folder.manage_addProduct['OFSP'].manage_addFolder(id=searched_object_id)
    self.getSkinnableObject().changeSkin(skinname=None)
    self.assertTrue(getattr(self.getSkinnableObject(), searched_object_id, None) is not None)
    self.assertTrue(getattr(tested_skin_folder,        searched_object_id, None) is not None)

  def test_03_deletedIsNotFound(self):
    searched_object_id = 'dummyFound'
    tested_skin_folder = self.getTestedSkinFolder()
    skinnable_object = self.getSkinnableObject()
    tested_skin_folder.manage_addProduct['OFSP'].manage_addFolder(id=searched_object_id)
    self.getSkinnableObject().changeSkin(skinname=None)
    # Access the object to make sure it is present in cache.
    self.assertTrue(getattr(skinnable_object,   searched_object_id, None) is not None)
    self.assertTrue(getattr(tested_skin_folder, searched_object_id, None) is not None)
    tested_skin_folder.manage_delObjects(ids=[searched_object_id,])
    self.getSkinnableObject().changeSkin(skinname=None)
    self.assertTrue(getattr(skinnable_object,   searched_object_id, None) is None)
    self.assertTrue(getattr(tested_skin_folder, searched_object_id, None) is None)

  def test_04_manageRenameObject(self):
    searched_object_id = 'dummyFound'
    searched_object_other_id = 'dummyFoundToo'
    tested_skin_folder = self.getTestedSkinFolder()
    skinnable_object = self.getSkinnableObject()
    tested_skin_folder.manage_addProduct['OFSP'].manage_addFolder(id=searched_object_id)
    # Commit transaction so that the created object gets a _p_jar, so it can be renamed.
    # See OFS.CopySupport:CopySource.cb_isMoveable()
    get_transaction().commit(1)
    self.getSkinnableObject().changeSkin(skinname=None)
    # Access the object to make sure it is present in cache.
    self.assertTrue(getattr(skinnable_object,   searched_object_id, None) is not None)
    self.assertTrue(getattr(tested_skin_folder, searched_object_id, None) is not None)
    tested_skin_folder.manage_renameObject(id=searched_object_id, new_id=searched_object_other_id)
    self.getSkinnableObject().changeSkin(skinname=None)
    self.assertTrue(getattr(skinnable_object,   searched_object_id, None) is None)
    self.assertTrue(getattr(tested_skin_folder, searched_object_id, None) is None)
    self.assertTrue(getattr(skinnable_object,   searched_object_other_id, None) is not None)
    self.assertTrue(getattr(tested_skin_folder, searched_object_other_id, None) is not None)

if __name__ == '__main__':
  unittest.main()
