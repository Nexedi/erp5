# -*- coding: latin1 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SARL and Contributors. All Rights Reserved.
#          Aurélien Calonne <aurel@nexedi.com>
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
from zLOG import LOG
from Products.CMFCore.tests.base.testcase import LogInterceptor
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
      self.folder = self.getPortal().newContent(id='TestFolder',
                                                portal_type='Folder')


    def beforeTearDown(self):
      """
        Executed after each test_*.
      """
      self.folder.manage_delObjects(ids=list(self.folder.objectIds()))
      self.getPortal().manage_delObjects(ids=[self.folder.getId(),])
      clearCache()
      get_transaction().commit()
      self.tic()      


    def newContent(self):
      """
        Create an object in self.folder and return it.
      """
      return self.folder.newContent(portal_type='Folder')
    
    def test_01_folderIsBtree(self, quiet=0, run=1):
      """
      Test the folder is a BTree
      """
      if not run : return
      if not quiet:
        message = 'Test folderIsBtree'
        LOG('Testing... ', 0, message)
      self.assertRaises(NotImplementedError, self.folder.getTreeIdList)
      self.assertEqual(self.folder.isBTree(), True)
      self.assertEqual(self.folder.isHBTree(), False)
      

    def test_02_migrateFolder(self, quiet=0, run=1):
      """
      migrate folder from btree to hbtree
      """
      if not run : return
      if not quiet:
        message = 'Test migrateFolder'
        LOG('Testing... ', 0, message)
      # Create some objects
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      obj1 = self.newContent()
      self.assertEquals(obj1.getId(), '1')
      obj2 = self.newContent()
      self.assertEquals(obj2.getId(), '2')
      obj3 = self.newContent()
      self.assertEquals(obj3.getId(), '3')
      get_transaction().commit()
      self.tic()      
      # call migration script
      self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                  new_generate_id_method="_generatePerDayId")
      get_transaction().commit()
      self.tic()
      # check we now have a hbtree
      self.assertEqual(self.folder.isBTree(), False)
      self.assertEqual(self.folder.isHBTree(), True)
      self.assertEqual(len(self.folder.getTreeIdList()), 1)
      self.assertEqual(len(self.folder.objectIds()), 3)
      # check params of objectIds in case of hbtree
      self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
      LOG("test", 300, "rien")
      self.assertEqual(len(self.folder.objectValues()), 3)
      LOG("test", 300, "base_id")
      self.assertEqual(len(self.folder.objectValues(base_id=None)), 0)
      # check object ids
      from DateTime import DateTime
      date = DateTime().Date()
      date = date.replace("/", "")
      self.assertEquals(obj1.getId(), '%s-1' %date)
      self.assertEquals(obj2.getId(), '%s-2' %date)
      self.assertEquals(obj3.getId(), '%s-3' %date)
      # add object and check its id
      obj4 = self.newContent()
      self.assertEquals(obj4.getId().split('-')[0], date)


    def test_03_emptyFolderIsBtree(self, quiet=0, run=1):
      """
      Test the folder is a BTree
      """
      if not run : return
      if not quiet:
        message = 'Test EmptyFolderIsBtree'
        LOG('Testing... ', 0, message)
      self.assertRaises(NotImplementedError, self.folder.getTreeIdList)
      self.assertEqual(self.folder.isBTree(), True)
      self.assertEqual(self.folder.isHBTree(), False)
      

    def test_04_migrateEmptyFolder(self, quiet=0, run=1):
      """
      migrate empty folder from btree to hbtree
      """
      if not run : return
      if not quiet:
        message = 'Test migrateEmptyFolder'
        LOG('Testing... ', 0, message)
      # Create some objects
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      self.assertEqual(len(self.folder.objectIds()), 0)      
      # call migration script
      self.folder.migrateToHBTree(migration_generate_id_method=None,
                                  new_generate_id_method="_generatePerDayId")
      get_transaction().commit()
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
      self.failUnless(date in obj1.getId())
      
    def test_05_migrateFolderWithoutIdChange(self, quiet=0, run=1):
      """
      migrate folder from btree to hbtree, do not touch ids
      """
      if not run : return
      # Create some objects
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      obj1 = self.newContent()
      self.assertEquals(obj1.getId(), '1')
      obj2 = self.newContent()
      self.assertEquals(obj2.getId(), '2')
      obj3 = self.newContent()
      self.assertEquals(obj3.getId(), '3')
      get_transaction().commit()
      self.tic()      
      # call migration script
      self.folder.migrateToHBTree()
      get_transaction().commit()
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
      self.assertEquals(obj1.getId(), '1')
      self.assertEquals(obj2.getId(), '2')
      self.assertEquals(obj3.getId(), '3')
      # add object and check its id
      obj4 = self.newContent()
      self.assertEquals(obj4.getId(), '4')

    def test_06_migrateFolderChangeIdGenerationMethodLater(self, quiet=0, run=1):
      """
      migrate folder from btree to hbtree, do not touch ids
      """
      if not run : return
      # Create some objects
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      obj1 = self.newContent()
      self.assertEquals(obj1.getId(), '1')
      obj2 = self.newContent()
      self.assertEquals(obj2.getId(), '2')
      obj3 = self.newContent()
      self.assertEquals(obj3.getId(), '3')
      get_transaction().commit()
      self.tic()      
      # call migration script
      self.folder.migrateToHBTree()
      get_transaction().commit()
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
      self.assertEquals(obj1.getId(), '1')
      self.assertEquals(obj2.getId(), '2')
      self.assertEquals(obj3.getId(), '3')
      # add object and check its id
      obj4 = self.newContent()
      self.assertEquals(obj4.getId(), '4')
      # set id generator
      id_generator_method = '_generatePerDayId'
      self.folder.setIdGenerator(id_generator_method)
      get_transaction().commit()
      self.assertEquals(self.folder.getIdGenerator(), id_generator_method)
      # check object ids
      self.assertEquals(obj1.getId(), '1')
      self.assertEquals(obj2.getId(), '2')
      self.assertEquals(obj3.getId(), '3')
      self.assertEquals(obj4.getId(), '4')
      # add object and check its id
      from DateTime import DateTime
      date = DateTime().Date()
      date = date.replace("/", "")
      
      obj5 = self.newContent()
      self.assertEquals(obj5.getId().split('-')[0], date)

    def test_07_migrateFolderTwice(self, quiet=0, run=1):
      """
      migrate folder twice from btree to hbtree
      """
      if not run : return
      if not quiet:
        message = 'Test migrateFolder'
        LOG('Testing... ', 0, message)
      # Create some objects
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      obj1 = self.newContent()
      self.assertEquals(obj1.getId(), '1')
      obj2 = self.newContent()
      self.assertEquals(obj2.getId(), '2')
      obj3 = self.newContent()
      self.assertEquals(obj3.getId(), '3')
      get_transaction().commit()
      self.tic()      
      # call migration script
      self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                  new_generate_id_method="_generatePerDayId")
      get_transaction().commit()
      self.tic()
      # check we now have a hbtree
      self.assertEqual(self.folder.isBTree(), False)
      self.assertEqual(self.folder.isHBTree(), True)
      self.assertEqual(len(self.folder.getTreeIdList()), 1)
      self.assertEqual(len(self.folder.objectIds()), 3)
      # check params of objectIds in case of hbtree
      self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
      LOG("test", 300, "rien")
      self.assertEqual(len(self.folder.objectValues()), 3)
      LOG("test", 300, "base_id")
      self.assertEqual(len(self.folder.objectValues(base_id=None)), 0)
      # check object ids
      from DateTime import DateTime
      date = DateTime().Date()
      date = date.replace("/", "")
      self.assertEquals(obj1.getId(), '%s-1' %date)
      self.assertEquals(obj2.getId(), '%s-2' %date)
      self.assertEquals(obj3.getId(), '%s-3' %date)
      # add object and check its id
      obj4 = self.newContent()
      self.assertEquals(obj4.getId().split('-')[0], date)
      # call migration script again
      self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                  new_generate_id_method="_generatePerDayId")
      get_transaction().commit()
      self.tic()
      
      # check object ids
      self.assertEquals(obj1.getId(), '%s-1' %date)
      self.assertEquals(obj2.getId(), '%s-2' %date)
      self.assertEquals(obj3.getId(), '%s-3' %date)
      self.assertEquals(obj4.getId().split('-')[0], date)
      
    def test_08_migrateFolderTwiceSimultaneously(self, quiet=0, run=1):
      """
      migrate folder twice from btree to hbtree
      """
      if not run : return
      if not quiet:
        message = 'Test migrateFolder'
        LOG('Testing... ', 0, message)
      # Create some objects
      self.assertEquals(self.folder.getIdGenerator(), '')
      self.assertEquals(len(self.folder), 0)
      obj1 = self.newContent()
      self.assertEquals(obj1.getId(), '1')
      obj2 = self.newContent()
      self.assertEquals(obj2.getId(), '2')
      obj3 = self.newContent()
      self.assertEquals(obj3.getId(), '3')
      get_transaction().commit()
      self.tic()      
      # call migration script twice
      self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                  new_generate_id_method="_generatePerDayId")
      get_transaction().commit()
      self.folder.migrateToHBTree(migration_generate_id_method="Base_generateIdFromStopDate",
                                  new_generate_id_method="_generatePerDayId")
      get_transaction().commit()
      self.tic()
      # check we now have a hbtree
      self.assertEqual(self.folder.isBTree(), False)
      self.assertEqual(self.folder.isHBTree(), True)
      self.assertEqual(len(self.folder.getTreeIdList()), 1)
      self.assertEqual(len(self.folder.objectIds()), 3)
      # check params of objectIds in case of hbtree
      self.assertEqual(len(self.folder.objectIds(base_id=None)), 0)
      LOG("test", 300, "rien")
      self.assertEqual(len(self.folder.objectValues()), 3)
      LOG("test", 300, "base_id")
      self.assertEqual(len(self.folder.objectValues(base_id=None)), 0)
      # check object ids
      from DateTime import DateTime
      date = DateTime().Date()
      date = date.replace("/", "")
      self.assertEquals(obj1.getId(), '%s-1' %date)
      self.assertEquals(obj2.getId(), '%s-2' %date)
      self.assertEquals(obj3.getId(), '%s-3' %date)
      # add object and check its id
      obj4 = self.newContent()
      self.assertEquals(obj4.getId().split('-')[0], date)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestFolderMigration))
  return suite
