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
    return ('erp5_crm',)
    #return ()

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getPersonModule(self):
    return getattr(self.getPortal(), 'person', None)

  def getOrganisationModule(self):
    return getattr(self.getPortal(), 'organisation', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def testHasEverything(self, quiet=0, run=run_all_test):
    # Test if portal_synchronizations was created
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoriesTool()!=None)
    self.failUnless(self.getPersonModule()!=None)
    self.failUnless(self.getOrganisationModule()!=None)

  def afterSetUp(self, quiet=1, run=1):
    self.login()
    portal = self.getPortal()
    portal.portal_types.constructContent(type_name='Person Module',
                                       container=portal,
                                       id='person')
    portal.portal_types.constructContent(type_name='Organisation Module',
                                       container=portal,
                                       id='organisation')
    person_module = self.getPersonModule()
    p1 = person_module.newContent(id=self.id1)
    organisation_module = self.getOrganisationModule()
    o1 = organisation_module.newContent(id=self.id1)
    portal_categories = self.getCategoriesTool()
    # This set the acquisition for region
    for bc in ('region', ):
      if not hasattr(portal_categories, bc):
        addBaseCategory(portal_categories, bc)
      portal_categories[bc].setAcquisitionBaseCategoryList('subordination',)
      portal_categories[bc].setAcquisitionPortalTypeList(['Address', 'Organisation', 'Person'])
      portal_categories[bc].setAcquisitionMaskValue(1)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionObjectIdList(['default_address'])


  def login(self, quiet=0, run=run_all_test):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def testSingleCategory(self, quiet=0, run=run_all_test):
    # Test if a single category is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Single Category ')
      LOG('Testing... ',0,'testSingleCategory')
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region1)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),[self.region1])

  def testMultipleCategory(self, quiet=0, run=run_all_test):
    # Test if multiple categories are working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Multiple Category ')
      LOG('Testing... ',0,'testMultipleCategory')
    portal = self.getPortal()
    region_value_list = [portal.portal_categories.resolveCategory(self.region1),
                         portal.portal_categories.resolveCategory(self.region2)]
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)

  def testCategoryValue(self, quiet=0, run=run_all_test):
    # Test if we can get categories values
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Category Value ')
      LOG('Testing... ',0,'testCategoryValue')
    portal = self.getPortal()
    region_value = portal.portal_categories.resolveCategory(self.region1)
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegionValue(),region_value)

  def testReturnNone(self, quiet=0, run=run_all_test):
    # Test if we getCategory return None if the cat is '' or None
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Return None ')
      LOG('Testing... ',0,'testReturnNone')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(None)
    self.assertEqual(p1.getRegion(),None)
    p1.setRegion('')
    self.assertEqual(p1.getRegion(),None)

  def testSingleAcquisition(self, quiet=0, run=run_all_test):
    # Test if the acquisition for a single value is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest Single Acquisition ')
      LOG('Testing... ',0,'testSingleAcquisition')
    portal = self.getPortal()
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1 = self.getPersonModule()._getOb(self.id1)
    o1.setRegion(self.region1)
    p1.setSubordinationValue(o1)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),[self.region1])

  def testListAcquisition(self, quiet=0, run=run_all_test):
    # Test if the acquisition for a single value is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\nTest List Acquisition ')
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
    output = ''
    result = portal.erp5_sql_connection.manage_test('select path from catalog')
    for line in result:
      output += '\n%s' % line['path']
    LOG('sql result',0,output)
    o_uid = p1.getUid()
    output = ''
    result = portal.erp5_sql_connection.manage_test('select * from category where uid=%s' % o_uid)
    cat_uid = ''
    for line in result:
      output += '\n%s' % line['uid']
      output += '\n%s' % line['category_uid']
      cat_uid = line['category_uid']
    LOG('sql2 result',0,output)
    result = portal.erp5_sql_connection.manage_test('select * from catalog where uid=%s' % cat_uid)
    output = ''
    for line in result:
      output += '\n%s' % line['path']
    LOG('sql3 result',0,output)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)





if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCMFCategory))
        return suite

