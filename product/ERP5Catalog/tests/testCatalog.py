##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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



#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
import time
import os
from Products.ERP5Type import product_path
from DateTime import DateTime

class Test(ERP5TypeTestCase):
  """
  This is the list of test

  test setNextStartDate : 
  - every hour
  - at 6, 10, 15, 21 every day
  - every day at 10
  - every 3 days at 14 and 15 and 17
  - every monday and friday, at 6 and 15
  - every 1st and 15th every month, at 12 and 14
  - every 1st day of every 2 month, at 6
  """

  def getTitle(self):
    return "ERP5Catalog"

  # Different variables used for this test
  run_all_test = 1
  source_company_id = 'Nexedi'
  destination_company_id = 'Coramy'
  component_id = 'brick'
  sales_order_id = '1'
  quantity = 10
  base_price = 0.7832

  #def populate(self, quiet=1, run=1):
  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    catalog_tool = self.getCatalogTool()
    # XXX This does not works
    #catalog_tool.reindexObject(portal)

    # First reindex
    #LOG('afterSetup',0,'portal.portal_categories.immediateReindexObject')
    #portal.portal_categories.immediateReindexObject()
    #LOG('afterSetup',0,'portal.portal_simulation.immediateReindexObject')
    #portal.portal_simulation.immediateReindexObject()

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def getSqlPathList(self):
    """
    Give the full list of path in the catalog
    """
    sql_connection = self.getSqlConnection()
    sql = 'select path from catalog'
    result = sql_connection.manage_test(sql)
    path_list = map(lambda x: x['path'],result)
    return path_list

  def checkRelativeUrlInSqlPathList(self,url_list):
    path_list = self.getSqlPathList()
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.failUnless(path in path_list)
      LOG('checkRelativeUrlInSqlPathList found path:',0,path)

  def checkRelativeUrlNotInSqlPathList(self,url_list):
    path_list = self.getSqlPathList()
    portal_id = self.getPortalId()
    for url in url_list:
      path = '/' + portal_id + '/' + url
      self.failUnless(path not in  path_list)
      LOG('checkRelativeUrlInSqlPathList not found path:',0,path)

  def test_01_HasEverything(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoryTool()!=None)
    self.failUnless(self.getSimulationTool()!=None)
    self.failUnless(self.getTypeTool()!=None)
    self.failUnless(self.getSqlConnection()!=None)
    self.failUnless(self.getCatalogTool()!=None)

  def test_02_EverythingCatalogued(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Everything Catalogued')
      LOG('Testing... ',0,'testEverythingCatalogued')
    portal_catalog = self.getCatalogTool()
    organisation_module_list = portal_catalog(portal_type='Organisation Module')
    self.assertEquals(len(organisation_module_list),1)

  def test_03_CreateAndDeleteObject(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      message = 'Test Create And Delete Objects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    portal_catalog = self.getCatalogTool()
    person_module = self.getPersonModule()
    person = person_module.newContent(id='1',portal_type='Person')
    path_list = ['person/1']
    self.checkRelativeUrlNotInSqlPathList(path_list)
    person.immediateReindexObject()
    self.checkRelativeUrlInSqlPathList(path_list)
    person_module.manage_delObjects('1')
    self.checkRelativeUrlNotInSqlPathList(path_list)
    # Now we will ask to immediatly reindex
    person = person_module.newContent(id='2',portal_type='Person',immediate_reindex=1)
    path_list = ['person/2']
    self.checkRelativeUrlInSqlPathList(path_list)
    person.immediateReindexObject()
    self.checkRelativeUrlInSqlPathList(path_list)
    person_module.manage_delObjects('2')
    self.checkRelativeUrlNotInSqlPathList(path_list)
    # Now we will try with the method deleteContent
    person = person_module.newContent(id='3',portal_type='Person')
    path_list = ['person/3']
    self.checkRelativeUrlNotInSqlPathList(path_list)
    person.immediateReindexObject()
    self.checkRelativeUrlInSqlPathList(path_list)
    person_module.deleteContent('3')
    self.checkRelativeUrlNotInSqlPathList(path_list)

  def test_04_SearchFolderWithDeletedObjects(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      message = 'Search Folder With Deleted Objects'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)
    person_module = self.getPersonModule()
    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)
    person = person_module.newContent(id='4',portal_type='Person',immediate_reindex=1)
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)
    person.immediateReindexObject()
    person_module.manage_delObjects('4')
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

  def test_05_SearchFolderWithImmediateReindexObject(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      message = 'Search Folder With Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

    person = person_module.newContent(id='4',portal_type='Person')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)
    
    person_module.manage_delObjects('4')
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

  def test_06_SearchFolderWithRecursiveImmediateReindexObject(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      message = 'Search Folder With Recursive Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Now we will try the same thing as previous test and look at searchFolder
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

    person = person_module.newContent(id='4',portal_type='Person')
    person_module.recursiveImmediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)
    
    person_module.manage_delObjects('4')
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals([],folder_object_list)

  def test_07_ClearCatalogAndTestNewContent(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Clear Catalog And Test New Content'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='4',portal_type='Person',immediate_reindex=1)
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)

  def test_08_ClearCatalogAndTestRecursiveImmediateReindexObject(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Clear Catalog And Test Recursive Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='4',portal_type='Person')
    person_module.recursiveImmediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)

  def test_09_ClearCatalogAndTestImmediateReindexObject(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Clear Catalog And Test Immediate Reindex Object'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='4',portal_type='Person')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder()]
    self.assertEquals(['4'],folder_object_list)

  def test_10_OrderedSearchFolder(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      message = 'Ordered Search Folder'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)

    person_module = self.getPersonModule()

    # Clear catalog
    portal_catalog = self.getCatalogTool()
    portal_catalog.manage_catalogClear()

    person = person_module.newContent(id='a',portal_type='Person',title='a',description='z')
    person.immediateReindexObject()
    person = person_module.newContent(id='b',portal_type='Person',title='a',description='y')
    person.immediateReindexObject()
    person = person_module.newContent(id='c',portal_type='Person',title='a',description='x')
    person.immediateReindexObject()
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder(sort_on=[('id','ascendign')])]
    self.assertEquals(['a','b','c'],folder_object_list)
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder(sort_on=[('title','ascendign'),('description','ascending')])]
    self.assertEquals(['c','b','a'],folder_object_list)
    folder_object_list = [x.getObject().getId() for x in person_module.searchFolder(sort_on=[('title','ascendign'),('description','descending')])]
    self.assertEquals(['a','b','c'],folder_object_list)

  def atest_99_BadCatalog(self, quiet=0, run=run_all_test):
    """
    We should make sure that if a catalog method fails,
    then we will have an error on the user interface.
    """
    if not run: return
    if not quiet:
      message = 'Test Bad Catalog'
      ZopeTestCase._print('\n%s ' % message)
      LOG('Testing... ',0,message)





if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(Test))
        return suite

