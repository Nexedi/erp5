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

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.Base import _aq_reset
from AccessControl.SecurityManagement import newSecurityManager

class TestERP5Category(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  portal_type = 'Organisation'
  base_cat = 'abc'
  base_cat2 = 'efg'
  cat_list = [base_cat + '/1',base_cat + '/2']
  new_cat_list = [base_cat + '/3',base_cat + '/2']
  deep_cat_list = [base_cat + '/1/1',base_cat + '/2/1']
  new_deep_cat_list = [base_cat + '/3/1',base_cat + '/2/1']

  def getTitle(self):
    """
    """
    return "ERP5 Categories"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

    """
    return ('erp5_base',)

  def enableActivityTool(self):
    """
    You can override this. Return if we should create (1) or not (0) an activity tool
    """
    return 0

  def getPortalId(self):
    return self.getPortal().getId()

  def getOrderLine(self):
    return self.getSaleOrderModule()['1']['1']

  def getPredicate(self):
    return self.getSalePackingListModule()['1']

  def afterSetUp(self):
    self.login()
    # This add the base category size
    portal_categories = self.getCategoryTool()
    person_module = self.getPersonModule()
    bc = self.base_cat
    portal_categories.newContent(portal_type='Base Category',id=bc)
    self.cat1 = portal_categories[bc].newContent(id='1',portal_type='Category')
    self.deep_cat1 = self.cat1.newContent(id='1',portal_type='Category')
    self.cat2 = portal_categories[bc].newContent(id='2',portal_type='Category')
    self.deep_cat2 = self.cat2.newContent(id='1',portal_type='Category')
    portal_categories[self.base_cat].recursiveImmediateReindexObject()

    portal_type = self.getTypeTool()[self.portal_type]
    portal_type.base_category_list = [self.base_cat, self.base_cat2]
    # Reset aq dynamic
    _aq_reset()
    organisation_module = self.getOrganisationModule()
    self.organisation = organisation_module.newContent(id='1',portal_type=self.portal_type)
    self.organisation.immediateReindexObject()
    self.telephone = self.organisation.newContent(id='1',portal_type='Telephone')
    self.organisation2 = organisation_module.newContent(id='2',portal_type=self.portal_type)
    self.organisation2.immediateReindexObject()
    self.telephone2 = self.organisation2.newContent(id='1',portal_type='Telephone')
    self.person = person_module.newContent(portal_type = 'Person')
    self.person.immediateReindexObject()

    bc2 = self.base_cat2
    portal_categories.newContent(portal_type='Base Category',id=bc2)
    self.efg_l1=portal_categories[bc2].newContent(id='1',portal_type='Category')
    self.efg_l2=self.efg_l1.newContent(id='11',portal_type='Category')
    self.efg_l3=self.efg_l2.newContent(id='111',portal_type='Category')
    self.efg_l4=self.efg_l3.newContent(id='1111',portal_type='Category')
    portal_categories[self.base_cat2].recursiveImmediateReindexObject()

    # We have no place to put a Predicate, we will put it in the
    # Organisation Module
    portal = self.getPortal()
    type_tool = self.getTypeTool()
    module_type = type_tool['%s Module' % self.portal_type]
    module_type.allowed_content_types += ('Mapped Value',)
    module = self.getOrganisationModule()
    predicate = module.newContent(id='predicate',portal_type='Mapped Value')
    predicate.setCriterion('quantity',identity=None,min=None,max=None)
    predicate.immediateReindexObject()
    self.predicate = predicate

    get_transaction().commit(1) # If we don't commit, then we can't rename

  def login(self, quiet=0):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_01(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename Category')
    organisation = self.organisation
    organisation.setCategoryList(self.cat_list)
    self.failIfDifferentSet(organisation.getCategoryList(),self.cat_list)
    portal_categories = self.getCategoryTool()
    portal_categories[self.base_cat]['1'].edit(id='3')
    self.failIfDifferentSet(organisation.getCategoryList(),self.new_cat_list)

  def test_02(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename Category Tree')
    organisation = self.organisation
    organisation.setCategoryList(self.deep_cat_list)
    self.failIfDifferentSet(organisation.getCategoryList(),self.deep_cat_list)
    portal_categories = self.getCategoryTool()
    portal_categories[self.base_cat]['1'].edit(id='3')
    self.failIfDifferentSet(organisation.getCategoryList(),self.new_deep_cat_list)

  def test_03(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename Related Object')
    organisation = self.organisation
    organisation2 = self.organisation2
    organisation.setAbcValueList([organisation2])
    self.assertEquals(organisation.getAbcValueList(),[organisation2])
    self.assertEquals(organisation.getAbcIdList(),['2'])
    organisation2.edit(id='new_id')
    self.assertEquals(organisation.getAbcValueList(),[organisation2])
    self.assertEquals(organisation.getAbcIdList(),['new_id'])

  def test_04(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename Object With a related Sub Object')
    telephone2 = self.telephone2
    organisation = self.organisation
    organisation2 = self.organisation2
    organisation.setAbcValueList([telephone2])
    self.assertEquals(organisation.getAbcValueList(),[telephone2])
    self.assertEquals(organisation.getAbcList(),[telephone2.getRelativeUrl()])
    organisation2.edit(id='new_id')
    self.assertEquals(organisation.getAbcValueList(),[telephone2])
    self.assertEquals(organisation.getAbcList(),[telephone2.getRelativeUrl()])

  def test_05(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename Membership Criterion Category')
    predicate = self.predicate
    predicate.setMembershipCriterionBaseCategoryList(self.base_cat)
    predicate.setMembershipCriterionCategoryList(self.cat_list)
    self.failIfDifferentSet(predicate.getMembershipCriterionCategoryList(),self.cat_list)
    portal_categories = self.getCategoryTool()
    portal_categories[self.base_cat]['1'].edit(id='3')
    self.failIfDifferentSet(predicate.getMembershipCriterionCategoryList(),self.new_cat_list)

  def test_06(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename Module With an Object Related to an Object it Contains')
    organisation_module = self.getOrganisationModule()
    organisation = self.organisation
    person = self.person
    person.setSubordinationValue(organisation)
    self.assertEquals(person.getSubordinationValue(),organisation)
    organisation_module.edit(id='new_id')
    self.assertEquals(person.getSubordinationValue(),organisation)

  def test_07(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename a Base Category with a Person Related to a Sub-Sub-Sub-Category')
    o = self.organisation
    o.setEfgValueList([self.efg_l4])
    self.failIfDifferentSet(o.getEfgList(base=1),[self.base_cat2+'/1/11/111/1111'])
    self.efg_l1.edit(id='new_id')
    self.failIfDifferentSet(o.getEfgList(base=1),[self.base_cat2+'/new_id/11/111/1111'])

  def test_08(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Rename a Module with Contained Objects Refering to Other Objects inside the Same Module')
    om = self.getOrganisationModule()
    om['1'].setAbcValue(om['2'])
    om['1'].immediateReindexObject()
    self.assertEquals(len(om['2'].getRelatedValueList('abc')), 1)
    self.assertEquals(len(om['2'].Base_zSearchRelatedObjectsByCategory(category_uid = om['2'].getUid())),1)    
    self.assertEquals(om['1'].getAbc(),om['2'].getRelativeUrl())
    original_uid = om['2'].getUid()
    om.edit(id='new_id')
    om = self.getPortal()['new_id']
    self.assertEquals(original_uid, om['2'].getUid())
    self.assertEquals(len(om['2'].getRelatedValueList('abc')), 1)
    self.assertEquals(len(om['2'].Base_zSearchRelatedObjectsByCategory(category_uid = om['2'].getUid())),1)
    self.assertEquals(om['1'].getAbc(),om['2'].getRelativeUrl())

  def test_08(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Make sure Base_viewDict is working for categories with sub categories')
    portal_categories = self.getCategoryTool()
    base_category = portal_categories.activity
    self.assertTrue(len(base_category.Base_viewDict())>0)
    base_category.newContent(id='toto',title='Toto')
    self.assertTrue(len(base_category.Base_viewDict())>0)

if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestERP5Category))
        return suite

