# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007,2009 Nexedi SA and Contributors. All Rights Reserved.
#          Aurélien Calonne <aurel@nexedi.com>
#          Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5Type.tests.utils import LogInterceptor
from Products.ERP5Type.Cache import clearCache

class TestFolderMigration(ERP5TypeTestCase, LogInterceptor):

  # Some helper methods

  def getTitle(self):
    return "Folder Migration"

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

  def beforeTearDown(self):
    """
      Executed after each test_*.
    """
    self.folder.manage_delObjects(ids=list(self.folder.objectIds()))
    self.portal.manage_delObjects(ids=[self.folder.getId(),])
    clearCache()
    self.tic()

  def newContent(self, *args, **kwargs):
    """
      Create an object in self.folder and return it.
    """
    return self.folder.newContent(portal_type='Folder', *args, **kwargs)

  def test_01_folderIsBtree(self):
    """
    Test the folder is a BTree
    """
    self.assertRaises(NotImplementedError, self.folder.getTreeIdList)
    self.assertEqual(self.folder.isBTree(), True)
    self.assertEqual(self.folder.isHBTree(), False)

  def test_02_migrateFolder(self):
    """
    migrate folder from btree to hbtree
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script
    self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                new_generate_id_method="_generatePerDayId")
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.getTreeIdList()), 1)
    self.assertEqual(len(self.folder.objectIds()), 3)
    # check params of objectIds in case of hbtree
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
    self.assertEqual(len(self.folder.objectValues()), 3)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 0)
    # check object ids
    from DateTime import DateTime
    date = DateTime().Date()
    date = date.replace("/", "")
    self.assertEqual(obj1.getId(), '%s-1' %date)
    self.assertEqual(obj2.getId(), '%s-2' %date)
    self.assertEqual(obj3.getId(), '%s-3' %date)
    # add object and check its id
    obj4 = self.newContent()
    self.assertEqual(obj4.getId().split('-')[0], date)

  def test_03_emptyFolderIsBtree(self):
    """
    Test the folder is a BTree
    """
    self.assertRaises(NotImplementedError, self.folder.getTreeIdList)
    self.assertEqual(self.folder.isBTree(), True)
    self.assertEqual(self.folder.isHBTree(), False)

  def test_03a_filledFolderIsBtree(self):
    """
    Test the folder is a BTree
    """
    self.folder.newContent()
    self.assertRaises(NotImplementedError, self.folder.getTreeIdList)
    self.assertEqual(self.folder.isBTree(), True)
    self.assertEqual(self.folder.isHBTree(), False)

  def test_04_migrateEmptyFolder(self):
    """
    migrate empty folder from btree to hbtree
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    self.assertEqual(len(self.folder.objectIds()), 0)
    # call migration script
    self.folder.migrateToHBTree(migration_generate_id_method=None,
                                new_generate_id_method="_generatePerDayId")
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.objectIds()), 0)
    # check new object ids
    obj1 = self.newContent()
    from DateTime import DateTime
    date = DateTime().Date()
    date = date.replace("/", "")
    self.assertTrue(date in obj1.getId())
    # check we still have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.objectIds()), 1)

  def test_05_migrateFolderWithoutIdChange(self):
    """
    migrate folder from btree to hbtree, do not touch ids
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script with explicit new_generate_id_method (so migration code
    # doesn't assign a good default
    self.folder.migrateToHBTree(new_generate_id_method='_generateNextId')
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.getTreeIdList()), 1)
    self.assertEqual(len(self.folder.objectIds()), 3)
    # check params of objectIds in case of hbtree
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 3)
    self.assertEqual(len(self.folder.objectValues()), 3)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 3)
    # check object ids
    self.assertEqual(obj1.getId(), '1')
    self.assertEqual(obj2.getId(), '2')
    self.assertEqual(obj3.getId(), '3')
    # add object and check its id
    obj4 = self.newContent()
    self.assertEqual(obj4.getId(), '4')

  def test_06_migrateFolderChangeIdGenerationMethodLater(self):
    """
    migrate folder from btree to hbtree, do not touch ids
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script with explicit new_generate_id_method (so migration code
    # doesn't assign a good default
    self.folder.migrateToHBTree(new_generate_id_method='_generateNextId')
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.getTreeIdList()), 1)
    self.assertEqual(len(self.folder.objectIds()), 3)
    # check params of objectIds in case of hbtree
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 3)
    self.assertEqual(len(self.folder.objectValues()), 3)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 3)
    # check object ids
    self.assertEqual(obj1.getId(), '1')
    self.assertEqual(obj2.getId(), '2')
    self.assertEqual(obj3.getId(), '3')
    # add object and check its id
    obj4 = self.newContent()
    self.assertEqual(obj4.getId(), '4')
    # set id generator
    id_generator_method = '_generatePerDayId'
    self.folder.setIdGenerator(id_generator_method)
    self.commit()
    self.assertEqual(self.folder.getIdGenerator(), id_generator_method)
    # check object ids
    self.assertEqual(obj1.getId(), '1')
    self.assertEqual(obj2.getId(), '2')
    self.assertEqual(obj3.getId(), '3')
    self.assertEqual(obj4.getId(), '4')
    # add object and check its id
    from DateTime import DateTime
    date = DateTime().Date()
    date = date.replace("/", "")

    obj5 = self.newContent()
    self.assertEqual(obj5.getId().split('-')[0], date)

  def test_07_migrateFolderTwice(self):
    """
    migrate folder twice from btree to hbtree
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script
    self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                new_generate_id_method="_generatePerDayId")
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.getTreeIdList()), 1)
    self.assertEqual(len(self.folder.objectIds()), 3)
    # check params of objectIds in case of hbtree
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
    self.assertEqual(len(self.folder.objectValues()), 3)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 0)
    # check object ids
    from DateTime import DateTime
    date = DateTime().Date()
    date = date.replace("/", "")
    self.assertEqual(obj1.getId(), '%s-1' %date)
    self.assertEqual(obj2.getId(), '%s-2' %date)
    self.assertEqual(obj3.getId(), '%s-3' %date)
    # add object and check its id
    obj4 = self.newContent()
    self.assertEqual(obj4.getId().split('-')[0], date)
    # call migration script again
    self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                new_generate_id_method="_generatePerDayId")
    self.tic()

    # check object ids
    self.assertEqual(obj1.getId(), '%s-1' %date)
    self.assertEqual(obj2.getId(), '%s-2' %date)
    self.assertEqual(obj3.getId(), '%s-3' %date)
    self.assertEqual(obj4.getId().split('-')[0], date)

  def test_08_migrateFolderTwiceSimultaneously(self):
    """
    migrate folder twice from btree to hbtree, simultaneously
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script twice
    self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                new_generate_id_method="_generatePerDayId")
    self.commit()
    self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                new_generate_id_method="_generatePerDayId")
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.getTreeIdList()), 1)
    self.assertEqual(len(self.folder.objectIds()), 3)
    # check params of objectIds in case of hbtree
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
    self.assertEqual(len(self.folder.objectValues()), 3)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 0)
    # check object ids
    from DateTime import DateTime
    date = DateTime().Date()
    date = date.replace("/", "")
    self.assertEqual(obj1.getId(), '%s-1' %date)
    self.assertEqual(obj2.getId(), '%s-2' %date)
    self.assertEqual(obj3.getId(), '%s-3' %date)
    # add object and check its id
    obj4 = self.newContent()
    self.assertEqual(obj4.getId().split('-')[0], date)

  def test_09_migrateFolderCreateNewObjectAtOnce(self):
    """
    migrate folder from btree to hbtree, create object with base, without any
    previous checks
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script
    self.folder.migrateToHBTree()
    self.tic()
    obj4 = self.newContent(id='BASE-123')
    self.assertEqual(obj4.getId(), 'BASE-123')
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 3)
    self.assertEqual(len(self.folder.objectValues()), 4)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 3)
    self.assertEqual(len(self.folder.objectIds(base_id='BASE')), 1)
    self.assertEqual(len(self.folder.objectValues(base_id='BASE')), 1)

  def test_10_migrateFolderCreateMoreObjectAtOnceDifferentBase(self):
    """
    migrate folder from btree to hbtree, create objects with two bases,
    without any previous checks
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent()
    self.assertEqual(obj3.getId(), '3')
    self.tic()
    # call migration script
    self.folder.migrateToHBTree()
    self.tic()
    obj4 = self.newContent(id='BASE-123')
    obj5 = self.newContent(id='BASE-BELONG-123')
    self.assertEqual(obj4.getId(), 'BASE-123')
    self.assertEqual(obj5.getId(), 'BASE-BELONG-123')
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 3)
    self.assertEqual(len(self.folder.objectValues()), 5)
    self.assertEqual(len(self.folder.objectValues(base_id=None)), 3)
    self.assertEqual(len(self.folder.objectIds(base_id='BASE')), 1)
    self.assertEqual(len(self.folder.objectValues(base_id='BASE')), 1)
    self.assertEqual(len(self.folder.objectIds(base_id='BASE-BELONG')), 1)
    self.assertEqual(len(self.folder.objectValues(base_id='BASE-BELONG')), 1)

  def test_11_folderInMigratedFolderIsBTree(self):
    """
    Test the folder in HBTree folder is a BTree
    """
    self.folder.migrateToHBTree()
    self.tic()
    infolder = self.newContent()

    self.assertRaises(NotImplementedError, infolder.getTreeIdList)
    self.assertEqual(infolder.isBTree(), True)
    self.assertEqual(infolder.isHBTree(), False)

  def test_12_migrateFolderWithGoodIdsInIt(self):
    """
    migrate folder from btree to hbtree folder, which already has ids
    HBTree-friendly
    """
    id_prefix = 'BASE'
    obj1_id = '%s-1'%(id_prefix,)
    obj2_id = '%s-2'%(id_prefix,)
    obj3_id = '%s-3'%(id_prefix,)
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    self.newContent(id=obj1_id)
    self.newContent(id=obj2_id)
    self.newContent(id=obj3_id)
    self.tic()
    # call migration script
    self.folder.migrateToHBTree()
    self.tic()
    # check we now have a hbtree
    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)
    self.assertEqual(len(self.folder.getTreeIdList()), 1)
    self.assertEqual(len(self.folder.objectIds()), 3)
    # check params of objectIds in case of hbtree
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
    self.assertEqual(len(self.folder.objectValues()), 3)
    self.assertEqual(len(self.folder.objectValues(base_id=id_prefix)), 3)
    # add object without base
    obj4 = self.newContent(id='1')
    self.assertEqual(obj4.getId(), '1')
    self.assertEqual(len(self.folder.objectIds(base_id=None)), 1)
    self.assertEqual(len(self.folder.objectValues()), 4)
    self.assertEqual(len(self.folder.objectValues(base_id=id_prefix)), 3)

  def test_13_wrongFolderHandlerFix(self):
    self.assertEqual(self.folder.isBTree(), True)
    self.assertEqual(self.folder.isHBTree(), False)

    self.folder._folder_handler = 'CMFBTreeFolderHandler'
    self.tic()

    self.assertEqual(self.folder.isHBTree(), False)

    self.assertEqual(self.folder._fixFolderHandler(), True)
    self.commit()

    self.assertEqual(self.folder.isBTree(), True)
    self.assertEqual(self.folder.isHBTree(), False)

    self.folder.migrateToHBTree()
    self.tic()

    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)

  def test_14_wrongFolderHandlerMigrate(self):
    self.assertEqual(self.folder.isBTree(), True)
    self.assertEqual(self.folder.isHBTree(), False)

    self.folder._folder_handler = 'CMFBTreeFolderHandler'
    self.tic()

    self.assertEqual(self.folder.isHBTree(), False)

    self.folder.migrateToHBTree()
    self.tic()

    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)

    self.folder.newContent()
    self.tic()

    self.assertEqual(self.folder.isBTree(), False)
    self.assertEqual(self.folder.isHBTree(), True)

  def test_15_checkMigrationWorksIfIdsDontChange(self):
    """
    migrate folder using a script that leaves some objects with same ids
    """
    # Create some objects
    self.assertEqual(self.folder.getIdGenerator(), '')
    self.assertEqual(len(self.folder), 0)
    obj1 = self.newContent()
    self.assertEqual(obj1.getId(), '1')
    obj2 = self.newContent()
    self.assertEqual(obj2.getId(), '2')
    obj3 = self.newContent(id='custom-id')
    self.assertEqual(obj3.getId(), 'custom-id')
    self.tic()
    # call migration script Base_generateIdFromCreationDate that only changes int ids
    self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromCreationDate",
                                new_generate_id_method="_generatePerDayId")
    self.tic()
    # check object ids
    from DateTime import DateTime
    date = DateTime().Date()
    date = date.replace("/", "")
    #1 y 2 should have new format id (because old ids were int)
    self.assertEqual(obj1.getId(), '%s-1' % date)
    self.assertEqual(obj2.getId(), '%s-2' % date)
    #3 should have the same old id
    self.assertEqual(obj3.getId(), 'custom-id')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFolderMigration))
  return suite
