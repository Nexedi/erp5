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
from zLOG import LOG
import time

class TestCMFCategory(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  id1 = '1'
  id2 = '2'
  region1 = 'europe/west/france'
  region2 = 'europe/west/germany'
  region_list = [region1, region2]

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template crm give the following things :
      modules:
        - person
        - organisation
      base categories:
        - region
        - subordination

      /organisation
    """
    return ('erp5_core',)
    #return ()

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def test_00_HasEverything(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoriesTool()!=None)
    self.failUnless(self.getPersonModule()!=None)
    self.failUnless(self.getOrganisationModule()!=None)

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    person_module = self.getPersonModule()
    p1 = person_module.newContent(id=self.id1)
    sub_person = p1.newContent(id=self.id1,portal_type='Person')
    p2 = person_module.newContent(id=self.id2)
    organisation_module = self.getOrganisationModule()
    o1 = organisation_module.newContent(id=self.id1)
    o2 = organisation_module.newContent(id=self.id2)
    portal_categories = self.getCategoriesTool()
    # This set the acquisition for region
    for bc in ('region', ):
      if not hasattr(portal_categories, bc):
        addBaseCategory(portal_categories, bc)
      portal_categories[bc].setAcquisitionBaseCategoryList(('subordination','parent'))
      portal_categories[bc].setAcquisitionPortalTypeList(['Address', 'Organisation', 'Person'])
      portal_categories[bc].setAcquisitionMaskValue(1)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionObjectIdList(['default_address'])
    for bc in ('subordination', ):
      if not hasattr(portal_categories, bc):
        addBaseCategory(portal_categories, bc)
      portal_categories[bc].setAcquisitionPortalTypeList(['Career', 'Organisation'])
      portal_categories[bc].setAcquisitionMaskValue(0)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionSyncValue(1)
      portal_categories[bc].setAcquisitionObjectIdList(['default_career'])
    for bc in ('group', ):
      if not hasattr(portal_categories, bc):
        addBaseCategory(portal_categories, bc)
      portal_categories[bc].setAcquisitionMaskValue(0)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionSyncValue(1)
      portal_categories[bc].setFallbackBaseCategoryList(['subordination'])

  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_01_SingleCategory(self, quiet=0, run=run_all_test):
    # Test if a single category is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Single Category ')
      LOG('Testing... ',0,'testSingleCategory')
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region1)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),[self.region1])

  def test_02_MultipleCategory(self, quiet=0, run=run_all_test):
    # Test if multiple categories are working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Multiple Category ')
      LOG('Testing... ',0,'testMultipleCategory')
    portal = self.getPortal()
    region_value_list = [portal.portal_categories.resolveCategory(self.region1),
                         portal.portal_categories.resolveCategory(self.region2)]
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)

  def test_03_CategoryValue(self, quiet=0, run=run_all_test):
    # Test if we can get categories values
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Category Value ')
      LOG('Testing... ',0,'testCategoryValue')
    portal = self.getPortal()
    region_value = portal.portal_categories.resolveCategory(self.region1)
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegionValue(),region_value)

  def test_04_ReturnNone(self, quiet=0, run=run_all_test):
    # Test if we getCategory return None if the cat is '' or None
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Return None ')
      LOG('Testing... ',0,'testReturnNone')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(None)
    self.assertEqual(p1.getRegion(),None)
    p1.setRegion('')
    self.assertEqual(p1.getRegion(),None)

  def test_05_SingleAcquisition(self, quiet=0, run=run_all_test):
    # Test if the acquisition for a single value is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Single Acquisition ')
      LOG('Testing... ',0,'testSingleAcquisition')
    portal = self.getPortal()
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1 = self.getPersonModule()._getOb(self.id1)
    o1.setRegion(self.region1)
    p1.setSubordinationValue(o1)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),[self.region1])

  def test_06_ListAcquisition(self, quiet=0, run=run_all_test):
    # Test if the acquisition for a single value is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test List Acquisition ')
      LOG('Testing... ',0,'testListAcquisition')
    portal = self.getPortal()
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1 = self.getPersonModule()._getOb(self.id1)
    o1.setRegion(self.region_list)
    p1.setSubordinationValue(o1)
    test = p1.getSubordinationValue()
    LOG('Testing... getSubordinationValue',0,test)
    sub = p1.getSubordinationValue()
    self.assertEqual(sub,o1)
    p1.immediateReindexObject()
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)

  def test_07_SubordinationValue(self, quiet=0, run=run_all_test):
    # Test if an infinite loop of the acquisition for a single value is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Subordination Value ')
      LOG('Testing... ',0,'testSubordinationValue')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1.setSubordinationValue(o1)
    p1.setRegion(None)
    self.assertEqual(p1.getSubordinationValue(),o1)
    self.assertEqual(p1.getDefaultSubordinationValue(),o1)
    self.assertEqual(p1.getSubordinationValueList(),[o1])

  def test_08_SubordinationMultipleValue(self, quiet=0, run=run_all_test):
    # Test if an infinite loop of the acquisition for a single value is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Subordination Multiple Value ')
      LOG('Testing... ',0,'testSubordinationMultipleValue')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    o2 = self.getOrganisationModule()._getOb(self.id2)
    subordination_value_list = [o1,o2]
    p1.setSubordinationValueList(subordination_value_list)
    p1.setRegion(None)
    self.assertEqual(p1.getSubordinationValue(),o1)
    self.assertEqual(p1.getDefaultSubordinationValue(),o1)
    self.assertEqual(p1.getSubordinationValueList(),subordination_value_list)

  def test_09_GetCategoryParentUidList(self, quiet=0, run=run_all_test):
    # Test if an infinite loop of the acquisition for a single value is working
    # WARNING: getCategoryParentUidList does not provide a sorted result
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Get Category Parent Uid List ')
      LOG('Testing... ',0,'testGetCategoryParentUidList')
    portal = self.getPortal()
    portal_categories = self.getCategoriesTool()
    # Create a base category basecat
    portal_categories.manage_addProduct['ERP5'].addBaseCategory('basecat')
    # Create a category cat1 at basecate
    portal_categories.basecat.manage_addProduct['ERP5'].addCategory('cat1')
    basecat = portal_categories.basecat
    cat1 = portal_categories.basecat.cat1
    # Create a category cat2 at cat1
    portal_categories.basecat.cat1.manage_addProduct['ERP5'].addCategory('cat2')
    cat2 = portal_categories.basecat.cat1.cat2
    # Compare result after sorting it
    parent_uid_list = [(cat2.getUid(), basecat.getUid(), 1),
                       (cat1.getUid(), basecat.getUid(), 0),
                       (basecat.getUid(), basecat.getUid(), 0)]
    parent_uid_list.sort()                       
    parent_uid_list2 = cat2.getCategoryParentUidList(relative_url = cat2.getRelativeUrl())
    parent_uid_list2.sort()
    self.assertEqual(parent_uid_list2, parent_uid_list)
    
  def test_10_FallBackBaseCategory(self, quiet=0, run=run_all_test):
    # Test if we can use an alternative base category
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Fallback Base Category ')
      LOG('Testing... ',0,'testFallbackBaseCategory')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    p2 = self.getPersonModule()._getOb(self.id2)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    self.assertEqual(p1.getGroupValue(),None)
    p1.setSubordinationValue(o1)
    p1.immediateReindexObject()
    o1.immediateReindexObject() # New ZSQLCatalog provides instant uid but does not reindex
    self.assertEqual(p1.getGroupValue(),o1)

  def test_11_ParentAcquisition(self, quiet=0, run=run_all_test):
    # Test if we can use an alternative base category
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Parent Acquisition ')
      LOG('Testing... ',0,'testParentAcquisition')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    self.assertEqual(p1.getRegion(),None)
    sub_person = p1._getOb(self.id1)
    self.assertEqual(sub_person.getRegion(),None)
    p1.setRegion(self.region1)
    p1.immediateReindexObject()
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(sub_person.getRegion(),self.region1)

  def test_12_GetRelatedValueAndValueList(self, quiet=0, run=run_all_test):
    # Test if an infinite loop of the acquisition for a single value is working
    # Typical error results from bad brain (do not copy, use aliases for zsqlbrain.py)
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Get Related Value And Value List ')
      LOG('Testing... ',0,'testGetRelatedValueAndValueList')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    p2 = self.getPersonModule()._getOb(self.id2)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1.setGroupValue(o1)
    p1.immediateReindexObject()
    o1.immediateReindexObject() # New ZSQLCatalog provides instant uid but does not reindex
    self.tic() # This is required 

    self.assertEqual(p1.getGroupValue(),o1)
    self.assertEqual(o1.getGroupRelatedValueList(),[p1])
    p2.setGroupValue(o1) # reindex implicit
    p2.immediateReindexObject() 
    self.tic()

    self.assertEqual(len(o1.getGroupRelatedValueList()),2)


if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCMFCategory))
        return suite

