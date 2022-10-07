##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurelien Calonne <aurel@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from six.moves import range


class TestTrashTool(ERP5TypeTestCase):
  """
  Test the behaviour of TrashTool
  """
  run_all_test = 1
  quiet = 1

  def getTitle(self):
    return "Trash Tool"

  def enableActivityTool(self):
    """
    You can override this.
    Return if we should create (1) or not (0) an activity tool.
    """
    return 1

  def afterSetUp(self):
    uf = self.portal.acl_users
    uf._doAddUser('seb', self.newPassword(), ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def stepAddBaseCategory(self, sequence=None, sequence_list=None, **kw):
    """
    Add a BaseCategory
    """
    pc = self.getCategoryTool()
    base_category = pc.newContent(portal_type = 'Base Category')
    self.assertTrue(base_category is not None)
    sequence.edit(bc_id=base_category.getId())

  def stepAddCategories(self, sequence=None, sequence_list=None, **kw):
    """
    Add category to a base category
    """
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    category_list = []
    for _ in range(10):
      category = base_category.newContent(portal_type='Category')
      category_list.append(category.getId())
    sequence.edit(category_id_list=category_list)

  def stepAddFolder(self, sequence=None, sequence_list=None, **kw):
    """
    add OFS Folder to backup
    """
    ps = self.getPortalObject().portal_skins
    erp5_core = ps['erp5_core']
    erp5_core.manage_addFolder(id="image")
    image = erp5_core._getOb("image")
    image.manage_addFile(id="file")

  def stepCheckTrashToolExists(self, sequence=None, sequence_list=None, **kw):
    """
    Check existence of trash tool
    """
    self.assertIsNotNone(self.getTrashTool())

  def stepCreateTrashBin(self, sequence=None, sequence_list=None, **kw):
    """
    Create a trash bin
    """
    trash = self.getTrashTool()
    pt = self.getTemplateTool()
    bt_id = 'fake_id'
    n = 0
    while bt_id in pt.objectIds():
      n = n + 1
      bt_id = 'fake_id_%s' %(n)
    bt = pt.newContent(id=bt_id, portal_type="Business Template")
    self.assertTrue(bt is not None)
    trashbin = trash.newTrashBin(bt_title='fake_bin', bt=bt)
    self.assertTrue(trashbin is not None)
    self.assertIn('fake_bin', trashbin.getId())
    sequence.edit(trash_id=trashbin.getId())

  def stepCheckTrashBinIndexation(self, sequence=None, sequence_list=None, **kw):
    """
    Check trash bin is indexable and indexed
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    self.assertTrue(trashbin.isIndexable)
    self.assertTrue(trash.isSubtreeIndexable())
    self.assertFalse(trashbin.isSubtreeIndexable())
    trash_uid = trash.getUid()
    trashbin_uid = trashbin.getUid()
    self.assertNotEqual(trash_uid, None)
    self.assertNotEqual(trashbin_uid, None)
    self.assertItemsEqual(
      [
        x.path
        for x in self.portal.portal_catalog(
          uid=(trash_uid, trashbin_uid),
        )
      ],
      [
        trash.getPath(),
        trashbin.getPath(),
      ],
    )

  def stepCheckObjectNotBackup(self, sequence=None, sequence_list=None, **kw):
    """
    Check that base category has not been backup
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    self.assertTrue(trashbin is not None)
    self.assertEqual(len(list(trashbin.objectIds())), 0)

  def stepCheckObjectBackupWithoutSubObjects(self, sequence=None, sequence_list=None, **kw):
    """
    Check that base category has not been backup
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    self.assertTrue(trashbin is not None)
    trashbin_objects_list = list(trashbin.objectValues())
    self.assertTrue(len(trashbin_objects_list) > 0)
    self.assertEqual(len(trashbin_objects_list), 1)
    # get portal_catogories trash folder
    obj = trashbin_objects_list[0]
    self.assertEqual(obj.getId(), 'portal_categories_items')
    self.assertEqual(obj.getPortalType(), 'Trash Folder')
    self.assertEqual(obj.isIndexable, 0)
    # get backup base category
    cat_objects_list = list(obj.objectValues())
    self.assertEqual(len(cat_objects_list), 1)
    cat_object = cat_objects_list[0]
    bc_id = sequence.get('bc_id')
    self.assertEqual(cat_object.getId(), bc_id)
    self.assertEqual(cat_object.isIndexable, 0)
    self.assertEqual(cat_object.getPortalType(), 'Base Category')
    # check no subobjects
    subcat_objects_list = (cat_object.objectIds())
    self.assertEqual(len(subcat_objects_list), 0)

  def stepCheckObjectBackupWithSubObjects(self, sequence=None, sequence_list=None, **kw):
    """
    Check that base category has not been backup
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    self.assertIsNotNone(trashbin)
    # get category trash folder
    bc_id = sequence.get('bc_id')
    trashbin_objects_list = list(trashbin.objectValues())
    self.assertEqual(len(trashbin_objects_list), 1)
    obj = trashbin_objects_list[0]
    self.assertEqual(obj.getId(), 'portal_categories_items')
    self.assertEqual(obj.getPortalType(), 'Trash Folder')
    self.assertEqual(obj.isIndexable, 0)
    # get base category backup
    cat_objects_list = list(obj.objectValues())
    self.assertEqual(len(cat_objects_list), 1)
    cat_object = cat_objects_list[0]
    bc_id = sequence.get('bc_id')
    self.assertEqual(cat_object.getId(), bc_id)
    self.assertEqual(cat_object.isIndexable, 0)
    self.assertEqual(cat_object.getPortalType(), 'Base Category')
    # check subobject list
    subcat_objects_list = (cat_object.objectIds())
    self.assertNotEqual(len(subcat_objects_list), 0)
    categ_id_list = sequence.get('category_id_list')
    for id_ in subcat_objects_list:
      self.assertIn(id_, categ_id_list)
      cat = cat_object._getOb(id_, None)
      self.assertTrue(cat.isIndexable)
      self.assertEqual(cat.getPortalType(), 'Category')

  def stepCheckFolderObjectBackup(self, sequence=None, sequence_list=None, **kw):
    """
    Check that skin folder has been well backup
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    self.assertTrue(trashbin is not None)
    trashbin_objects_list = list(trashbin.objectValues())
    self.assertTrue(len(trashbin_objects_list) > 0)
    self.assertEqual(len(trashbin_objects_list), 1)
    obj = trashbin_objects_list[0]
    self.assertEqual(obj.getId(), 'portal_skins_items')
    self.assertEqual(obj.getPortalType(), 'Trash Folder')
    self.assertEqual(obj.isIndexable, 0)
    # get backup OFS Folder
    skin_objects_list = list(obj.objectValues())
    self.assertEqual(len(skin_objects_list), 1)
    skin = skin_objects_list[0]
    self.assertEqual(skin.id, 'erp5_core')
    from OFS.Folder import Folder
    self.assertTrue(isinstance(skin, Folder))
    # get image folder
    skin_objects_list = list(skin.objectValues())
    self.assertEqual(len(skin_objects_list), 1)
    skin = skin_objects_list[0]
    self.assertEqual(skin.id, 'image')
    self.assertTrue(skin.getPortalType(), "Trash Folder")
    # get file
    f_objects_list = list(skin.objectValues())
    self.assertEqual(len(f_objects_list), 1)
    f = f_objects_list[0]
    self.assertEqual(f.getId(), 'file')
    self.assertTrue(f.getPortalType(), "Trash Folder")


  def stepBackupObjectsWithSave(self, sequence=None, sequence_list=None, **kw):
    """
    Backup objects and check subobjects are return
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    # get base category to backup
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    subobjects_ids = base_category.objectIds()
    bc_path = base_category.getPath().split('/')[2:-1]
    # check backup
    backup_subobjects_ids = trash.backupObject(trashbin, bc_path, bc_id, save=1)
    self.assertTrue(backup_subobjects_ids.keys().sort() == list(subobjects_ids).sort())

  def stepBackupFolderObjectsWithSave(self, sequence=None, sequence_list=None, **kw):
    """
    Backup objects and check subobjects are return
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    # backup the skin folder
    trash.backupObject(trashbin, ["portal_skins",], "erp5_core", save=1)
    # backup file
    trash.backupObject(trashbin, ["portal_skins", "erp5_core", "image"], "file", save=1)

  def stepBackupObjectsWithoutSave(self, sequence=None, sequence_list=None, **kw):
    """
    Backup objects and check subobjects are return
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    # get base category to backup
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    subobjects_ids = base_category.objectIds()
    bc_path = base_category.getPath().split('/')[1:-1]
    # check backup
    backup_subobjects_ids = trash.backupObject(trashbin, bc_path, bc_id, save=0)
    self.assertTrue(backup_subobjects_ids.keys().sort() == list(subobjects_ids).sort())

  def stepBackupObjectsWithKeepingSubobjects(self, sequence=None, sequence_list=None, **kw):
    """
    Backup objects and check subobjects are return
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    # get base category to backup
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    bc_path = base_category.getPath().split('/')[2:-1]
    # check backup
    backup_subobjects_ids = trash.backupObject(trashbin, bc_path, bc_id, save=1, keep_subobjects=1)
    # no subobjects return
    self.assertEqual(len(backup_subobjects_ids), 0)

  def stepBackupSubCategories(self, sequence=None, sequence_list=None, **kw):
    """
    Check we can add a trash folder into a backup object
    """
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    # get base category to backup
    subcat_path = sequence.get('subcat_path')
    bc_id = subcat_path.split('/')[-1]
    bc_path = subcat_path.split('/')[2:-1]
    # check backup
    trash.backupObject(trashbin, bc_path, bc_id, save=1)

  def stepAddSubCategories(self, sequence=None, sequence_list=None, **kw):
    # Add subcategories
    category_id_list = sequence.get('category_id_list')
    self.assertEqual(len(category_id_list), 10)
    cat_id = category_id_list[0]
    bc_id = sequence.get('bc_id')
    pc = self.getCategoryTool()
    base_category = pc._getOb(bc_id, None)
    self.assertTrue(base_category is not None)
    cat = base_category._getOb(cat_id, None)
    self.assertTrue(cat is not None)
    subcat = cat.newContent(portal_type='Category')
    self.assertTrue(subcat is not None)
    sequence.edit(subcat_path=subcat.getPath())

  def stepDeleteBaseCategory(self, sequence=None, sequence_list=None, **kw):
    pc = self.getCategoryTool()
    pc.manage_delObjects(ids=[sequence.get('bc_id')])

  def stepRestore(self, sequence=None, sequence_list=None, **kw):
    trash_id = sequence.get('trash_id')
    trash = self.getTrashTool()
    trashbin = trash._getOb(trash_id, None)
    bc_id = sequence.get('bc_id')
    trash.restoreObject(trashbin, ['portal_categories_items'], bc_id)

  def stepCheckRestore(self, sequence=None, sequence_list=None, **kw):
    bc_id = sequence.get('bc_id')
    bc = self.portal.portal_categories[bc_id]
    self.assertTrue(
      sorted(bc.objectIds()) == sorted(sequence.get('category_id_list'))
    )
    self.assertEqual(
      len(
        self.portal.portal_catalog(
          portal_type='Category',
          parent_uid=bc.getUid()
        )
      ), 10
    )

  # tests
  def test_01_checkTrashBinCreation(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check TrashBin Creation'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       Tic \
                       CheckTrashBinIndexation \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_02_checkBackupWithoutSave(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Backup Without Save'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       AddBaseCategory \
                       AddCategories \
                       Tic \
                       BackupObjectsWithoutSave \
                       CheckObjectNotBackup \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_03_checkBackupWithSave(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Backup With Save'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       AddBaseCategory \
                       AddCategories \
                       Tic \
                       BackupObjectsWithSave \
                       Tic \
                       CheckObjectBackupWithoutSubObjects \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_04_checkBackupWithSubObjects(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Backup Without Subobjects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       AddBaseCategory \
                       AddCategories \
                       Tic \
                       BackupObjectsWithKeepingSubobjects \
                       Tic \
                       CheckObjectBackupWithSubObjects \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_05_checkBackupWithTrashSubObjects(self, quiet=quiet, run=run_all_test):
    """
    Test we can backup a tree like this :
    base_category/trash_folder/category
    """
    if not run: return
    if not quiet:
      message = 'Test Check Backup With Trash Sub Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       AddBaseCategory \
                       AddCategories \
                       AddSubCategories \
                       Tic \
                       BackupObjectsWithSave \
                       Tic \
                       CheckObjectBackupWithoutSubObjects \
                       BackupSubCategories \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


  def test_06_checkBackupofOFSFolderWithSave(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Backup Of OFS Folder With Save'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       AddFolder \
                       Tic \
                       BackupFolderObjectsWithSave \
                       Tic \
                       CheckFolderObjectBackup \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_07_checkRestore(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Test Check Backup Without Subobjects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ', 0, message)
    sequence_list = SequenceList()
    sequence_string = '\
                       CheckTrashToolExists  \
                       CreateTrashBin \
                       AddBaseCategory \
                       AddCategories \
                       Tic \
                       BackupObjectsWithKeepingSubobjects \
                       Tic \
                       CheckObjectBackupWithSubObjects \
                       DeleteBaseCategory \
                       Tic \
                       Restore \
                       Tic \
                       CheckRestore \
                       '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTrashTool))
  return suite
