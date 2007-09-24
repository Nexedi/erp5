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

import unittest

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from zLOG import LOG

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TestCMFCategory(ERP5TypeTestCase):

  # Different variables used for this test
  run_all_test = 1
  quiet = 1
  id1 = '1'
  id2 = '2'
  region1 = 'europe/west/france'
  region2 = 'europe/west/germany'
  region_list = [region1, region2]

  def getTitle(self):
    return "CMFCategory"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

      the business template base give the following things :
      modules:
        - person
        - organisation
      base categories:
        - region
        - subordination

      /organisation
    """
    return ('erp5_base', 'erp5_trade')

  def getCategoriesTool(self):
    return getattr(self.getPortal(), 'portal_categories', None)

  def getPortalId(self):
    return self.getPortal().getId()

  def test_00_HasEverything(self, quiet=quiet, run=run_all_test):
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Has Everything ')
      LOG('Testing... ',0,'testHasEverything')
    self.failUnless(self.getCategoriesTool()!=None)
    self.failUnless(self.getPersonModule()!=None)
    self.failUnless(self.getOrganisationModule()!=None)

  def afterSetUp(self):
    self.login()
    portal = self.getPortal()

    # This test creates Person inside Person and Organisation inside
    # Organisation, so we modifiy type informations to allow anything inside
    # Person and Organisation (we'll cleanup on teardown)
    self.getTypesTool().getTypeInfo('Person').filter_content_types = 0
    organisation_ti = self.getTypesTool().getTypeInfo('Organisation')
    organisation_ti.filter_content_types = 0
    # we also enable 'destination' category on organisations
    self._organisation_categories = cat = organisation_ti.base_category_list
    organisation_ti.base_category_list = tuple(list(cat) + ['destination'])

    # Make persons.
    person_module = self.getPersonModule()
    if self.id1 not in person_module.objectIds():
      p1 = person_module.newContent(id=self.id1, title=self.id1)
    else:
      p1 = person_module._getOb(self.id1)
    if self.id1 not in p1.objectIds():
      sub_person = p1.newContent(id=self.id1,portal_type='Person')
    if self.id2 not in person_module.objectIds():
      p2 = person_module.newContent(id=self.id2, title=self.id2)
    # Make organisations.
    organisation_module = self.getOrganisationModule()
    if self.id1 not in organisation_module.objectIds():
      o1 = organisation_module.newContent(id=self.id1)
    if self.id2 not in organisation_module.objectIds():
      o2 = organisation_module.newContent(id=self.id2)
    portal_categories = self.getCategoriesTool()
    # Make a sale order and a sale packing list.
    sale_order_module = portal.sale_order_module
    if self.id1 not in sale_order_module.objectIds():
        sale_order_module.newContent(id=self.id1)
    sale_packing_list_module = portal.sale_packing_list_module
    if self.id1 not in sale_packing_list_module.objectIds():
        sale_packing_list_module.newContent(id=self.id1)
    # This set the acquisition for region
    for bc in ('region', ):
      if not hasattr(portal_categories, bc):
        portal_categories.newContent(portal_type='Base Category',id=bc)
      portal_categories[bc].setAcquisitionBaseCategoryList(('subordination','parent'))
      portal_categories[bc].setAcquisitionPortalTypeList("python: ['Address', 'Organisation', 'Person']")
      portal_categories[bc].setAcquisitionMaskValue(1)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionObjectIdList(['default_address'])
      if not 'europe' in portal_categories[bc].objectIds():
        portal_categories[bc].newContent(id='europe',portal_type='Category')
      big_region = portal_categories[bc]['europe']
      # Now we have to include by hand no categories
      if not 'west' in big_region.objectIds():
        big_region.newContent(id='west',portal_type='Category')
      region = big_region['west']
      if not 'france' in region.objectIds():
        region.newContent(id='france',portal_type='Category')
      if not 'germany' in region.objectIds():
        region.newContent(id='germany',portal_type='Category')
    for bc in ('subordination', ):
      if not hasattr(portal_categories, bc):
        portal_categories.newContent(portal_type='Base Category',id=bc)
      portal_categories[bc].setAcquisitionPortalTypeList("python: ['Career', 'Organisation']")
      portal_categories[bc].setAcquisitionMaskValue(0)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionSyncValue(1)
      portal_categories[bc].setAcquisitionObjectIdList(['default_career'])
    for bc in ('gender', ):
      if not hasattr(portal_categories, bc):
        portal_categories.newContent(portal_type='Base Category',id=bc)
      portal_categories[bc].setAcquisitionPortalTypeList("python: []")
      portal_categories[bc].setAcquisitionMaskValue(0)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      portal_categories[bc].setAcquisitionSyncValue(1)
      portal_categories[bc].setFallbackBaseCategoryList(['subordination'])

  def beforeTearDown(self):
    """Clean up."""
    # categories
    for bc in ('region', 'subordination', 'gender'):
      bc_obj = self.getPortal().portal_categories[bc]
      bc_obj.manage_delObjects()
    # type informations
    self.getTypesTool().getTypeInfo('Person').filter_content_types = 1
    organisation_ti = self.getTypesTool().getTypeInfo('Organisation')
    organisation_ti.filter_content_types = 1
    organisation_ti = self._organisation_categories

  def login(self):
    uf = self.getPortal().acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_01_SingleCategory(self, quiet=quiet, run=run_all_test):
    # Test if a single category is working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Single Category ')
      LOG('Testing... ',0,'testSingleCategory')
    o1 = self.getOrganisationModule()._getOb(self.id1)
    LOG('SingleCategory,',0,o1.getGenderRelatedValueList())

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region1)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),[self.region1])

  def test_02_MultipleCategory(self, quiet=quiet, run=run_all_test):
    # Test if multiple categories are working
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Multiple Category ')
      LOG('Testing... ',0,'testMultipleCategory')
    portal = self.getPortal()
    region_value_list = [portal.portal_categories.resolveCategory('region/%s' % self.region1),
                         portal.portal_categories.resolveCategory('region/%s' % self.region2)]
    self.assertNotEqual(None,region_value_list[0])
    self.assertNotEqual(None,region_value_list[1])
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)

  def test_03_CategoryValue(self, quiet=quiet, run=run_all_test):
    # Test if we can get categories values
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Category Value ')
      LOG('Testing... ',0,'testCategoryValue')
    portal = self.getPortal()
    region_value = portal.portal_categories.resolveCategory('region/%s' % self.region1)
    self.assertNotEqual(None,region_value)
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegionValue(),region_value)

  def test_isMemberOf(self):
    region_path = 'region/%s' % self.region1
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(None)
    self.failIf(p1.isMemberOf(region_path))
    p1.setRegion(self.region1)
    self.failUnless(p1.isMemberOf(region_path))

  def test_04_ReturnNone(self, quiet=quiet, run=run_all_test):
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

  def test_05_SingleAcquisition(self, quiet=quiet, run=run_all_test):
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

  def test_singleAcquisitionIsMemberOf(self):
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1 = self.getPersonModule()._getOb(self.id1)
    o1.setRegion(self.region1)
    p1.setSubordinationValue(o1)
    self.failUnless(p1.isMemberOf('region/%s' % self.region1))

  def test_06_ListAcquisition(self, quiet=quiet, run=run_all_test):
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
    sub = p1.getSubordinationValue()
    self.assertEqual(sub,o1)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)

  def test_listAcquisitionIsMemberOf(self):
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1 = self.getPersonModule()._getOb(self.id1)
    o1.setRegion(self.region_list)
    p1.setSubordinationValue(o1)
    self.failUnless(p1.isMemberOf('region/%s' % self.region1))

  def test_07_SubordinationValue(self, quiet=quiet, run=run_all_test):
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

  def test_08_SubordinationMultipleValue(self, quiet=quiet, run=run_all_test):
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

  def test_09_GetCategoryParentUidList(self, quiet=quiet, run=run_all_test):
    # Test if an infinite loop of the acquisition for a single value is working
    # WARNING: getCategoryParentUidList does not provide a sorted result
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Get Category Parent Uid List ')
      LOG('Testing... ',0,'testGetCategoryParentUidList')
    portal = self.getPortal()
    portal_categories = self.getCategoriesTool()
    # Create a base category basecat
    #portal_categories.manage_addProduct['ERP5'].addBaseCategory('basecat')
    portal_categories.newContent(portal_type='Base Category',id='basecat')
    # Create a category cat1 at basecate
    portal_categories.basecat.newContent(id='cat1',portal_type='Category')
    basecat = portal_categories.basecat
    cat1 = portal_categories.basecat.cat1
    # Create a category cat2 at cat1
    portal_categories.basecat.cat1.newContent(portal_type='Category',id='cat2')
    cat2 = portal_categories.basecat.cat1.cat2
    cat2.newContent(id='cat2',portal_type='Category')
    # Compare result after sorting it
    parent_uid_list = [(cat2.getUid(), basecat.getUid(), 1),
                       (cat1.getUid(), basecat.getUid(), 0),
                       (basecat.getUid(), basecat.getUid(), 0)]
    parent_uid_list.sort()
    parent_uid_list2 = cat2.getCategoryParentUidList(relative_url = cat2.getRelativeUrl())
    parent_uid_list2.sort()
    self.assertEqual(parent_uid_list2, parent_uid_list)

  def test_10_FallBackBaseCategory(self, quiet=quiet, run=run_all_test):
    # Test if we can use an alternative base category
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Fallback Base Category ')
      LOG('Testing... ',0,'testFallbackBaseCategory')
    portal = self.getPortal()
    p1 = self.getPersonModule()._getOb(self.id1)
    p2 = self.getPersonModule()._getOb(self.id2)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    self.assertEqual(p1.getGenderValue(),None)
    p1.setSubordinationValue(o1)
    self.assertEqual(p1.getGenderValue(),o1)

  def test_FallBackAcquisitionIsMemberOf(self):
    p1 = self.getPersonModule()._getOb(self.id1)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1.setSubordinationValue(o1)
    self.failUnless(p1.isMemberOf('gender/organisation_module/%s' % self.id1))

  def test_11_ParentAcquisition(self, quiet=quiet, run=run_all_test):
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
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(sub_person.getRegion(),self.region1)

  def test_parentAcquisitionIsMemberOf(self):
    p1 = self.getPersonModule()._getOb(self.id1)
    sub_person = p1._getOb(self.id1)
    p1.setRegion(self.region1)
    self.failUnless(p1.isMemberOf('region/%s' % self.region1))
    self.failUnless(sub_person.isMemberOf('region/%s' % self.region1))

  def test_parentAcquisitionIsMemberOfWithDifferentCategories(self):
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region1)
    sub_person = p1._getOb(self.id1)
    self.failUnless(p1.isMemberOf('region/%s' % self.region1))
    sub_person.setRegion(self.region2)
    self.failUnless(sub_person.isMemberOf('region/%s' % self.region2))

  def test_12_GetRelatedValueAndValueList(self, quiet=quiet, run=run_all_test):
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
    p1.setGenderValue(o1)
    get_transaction().commit()
    self.tic() # This is required

    self.assertEqual(p1.getGenderValue(),o1)
    self.assertEqual(o1.getGenderRelatedValueList(),[p1])
    p2.setGenderValue(o1) # reindex implicit
    get_transaction().commit()
    self.tic()

    self.assertEqual(len(o1.getGenderRelatedValueList()),2)

  def test_13_RenameCategory(self, quiet=quiet, run=run_all_test) :
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Category Renaming')
      LOG('Testing... ',0,'Category Renaming')

    portal = self.getPortal()
    france = portal.portal_categories.resolveCategory(
                                            'region/europe/west/france')
    self.assertNotEqual(france, None)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion('europe/west/france')
    get_transaction().commit()
    self.tic()

    west = portal.portal_categories.resolveCategory('region/europe/west')
    west.setId("ouest")
    get_transaction().commit()
    self.tic()

    self.assertEqual(west,
      portal.portal_categories.resolveCategory('region/europe/ouest'))
    self.assertEqual(p1.getRegion(), 'europe/ouest/france')
    self.failUnless(p1 in west.getRegionRelatedValueList())

  def test_13b_RenameCategoryUsingCutAndPaste(self, quiet=quiet, run=run_all_test) :
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Category Renaming with cut n paste')
      LOG('Testing... ',0,'Category Renaming')

    portal = self.getPortal()
    france = portal.portal_categories.resolveCategory(
                                            'region/europe/west/france')
    self.assertNotEqual(france, None)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion('europe/west/france')
    get_transaction().commit()
    self.tic()

    europe = portal.portal_categories.resolveCategory('region/europe')
    west = europe.west
    cb_data = europe.manage_cutObjects(['west'])
    portal.portal_categories.region.manage_pasteObjects(cb_data)
    get_transaction().commit()
    self.tic()

    self.assertEqual(west,
      portal.portal_categories.resolveCategory('region/west'))
    self.assertEqual(p1.getRegion(), 'west/france')
    self.failUnless(p1 in west.getRegionRelatedValueList())

  def test_13c_RenameCategoryUsingCutAndPasteButNotCopy(
                                        self, quiet=quiet, run=run_all_test) :
    if not run: return
    if not quiet:
      ZopeTestCase._print('\n Test Category Renaming with cut n paste, '
                          'copy n paste doesnt change')
      LOG('Testing... ',0,'Category Renaming')

    portal = self.getPortal()
    france = portal.portal_categories.resolveCategory(
                                    'region/europe/west/france')
    self.assertNotEqual(france, None)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion('europe/west/france')
    get_transaction().commit()
    self.tic()

    europe = portal.portal_categories.resolveCategory('region/europe')
    west = europe.west
    cb_data = europe.manage_copyObjects(['west'])
    portal.portal_categories.region.manage_pasteObjects(cb_data)
    get_transaction().commit()
    self.tic()

    self.assertEqual(west,
      portal.portal_categories.resolveCategory('region/europe/west'))
    self.assertEqual(p1.getRegion(), 'europe/west/france')
    # we are not member of the copy
    self.failUnless('west/france' not in p1.getRegionList())
    self.failUnless(p1 in west.getRegionRelatedValueList())


  def test_14_MultiplePortalTypes(self, quiet=quiet, run=run_all_test) :
    """ Checks that categories support different value per portal_type,
        like a colored graph on portal_type"""
    if not run: return
    if not quiet:
      message = 'Test multiple Portal Types for a same category'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    folder = self.getOrganisationModule()

    org_a = folder.newContent(portal_type='Organisation', id="org_a")
    org_b = folder.newContent(portal_type='Organisation', id="org_b")

    org_a.setDestinationValue(org_b)
    self.assertEqual(org_a.getDestinationValue(), org_b)

    pers_a = self.getPersonModule().newContent(
                  portal_type='Person', id='pers_a')

    for loop in range(3) :
      org_a.setDestinationValue(pers_a, portal_type='Person')
      self.assertEquals(
          org_a.getDestinationValue(portal_type='Person'), pers_a)
      self.assertEquals(
          org_a.getDestinationValue(portal_type='Organisation'), org_b)
      self.assertEquals(len(org_a.getDestinationValueList()), 2)

      org_a.setDestinationValue(org_b, portal_type='Organisation')
      self.assertEquals(
          org_a.getDestinationValue(portal_type='Person'), pers_a)
      self.assertEquals(
          org_a.getDestinationValue(portal_type='Organisation'), org_b)
      self.assertEquals(len(org_a.getDestinationValueList()), 2)

  def test_15_SortChildValues(self, quiet=quiet, run=run_all_test) :
    """ Checks on sorting child categories"""
    if not run: return
    if not quiet:
      message = 'Test Sort Child Values'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)

    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='sort_test')
    self.failUnless(bc is not None)
    bc.newContent(portal_type='Category', id='1', title='a', int_index=3)
    bc.newContent(portal_type='Category', id='2', title='b', int_index=1)
    bc.newContent(portal_type='Category', id='3', title='c', int_index=1)

    # simple sorting
    category_list = bc.getCategoryChildValueList(sort_on='title')
    self.assertEquals(len(category_list), 3)
    self.assertEquals(category_list[0].getId(), '1')
    self.assertEquals(category_list[1].getId(), '2')
    self.assertEquals(category_list[2].getId(), '3')

    # reverse sorting
    category_list = bc.getCategoryChildValueList(sort_on='title', sort_order='reverse')
    self.assertEquals(len(category_list), 3)
    self.assertEquals(category_list[0].getId(), '3')
    self.assertEquals(category_list[1].getId(), '2')
    self.assertEquals(category_list[2].getId(), '1')

    # another reverse sorting
    category_list = bc.getCategoryChildValueList(sort_on=(('title', 'reverse'),))
    self.assertEquals(len(category_list), 3)
    self.assertEquals(category_list[0].getId(), '3')
    self.assertEquals(category_list[1].getId(), '2')
    self.assertEquals(category_list[2].getId(), '1')

    # multiple sort parameters
    category_list = bc.getCategoryChildValueList(sort_on=('int_index', 'title'))
    self.assertEquals(len(category_list), 3)
    self.assertEquals(category_list[0].getId(), '2')
    self.assertEquals(category_list[1].getId(), '3')
    self.assertEquals(category_list[2].getId(), '1')

    # another multiple sort parameters
    category_list = bc.getCategoryChildValueList(sort_on=(('int_index', 'reverse'), 'title'))
    self.assertEquals(len(category_list), 3)
    self.assertEquals(category_list[0].getId(), '1')
    self.assertEquals(category_list[1].getId(), '2')
    self.assertEquals(category_list[2].getId(), '3')

  def test_16_GetRelatedValues(self, quiet=quiet, run=run_all_test) :
    """ Checks on getting related values"""
    if not run: return
    if not quiet:
      message = 'Test Get Related Values'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)

    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='related_value_test')
    self.failUnless(bc is not None)
    get_transaction().commit()
    self.tic()
    # A newly created base category should be referred to only by itself
    value_list = pc.getRelatedValueList(bc)
    self.assertEquals(len(value_list), 1)

    c = bc.newContent(portal_type='Category', id='1')
    self.failUnless(c is not None)
    get_transaction().commit()
    self.tic()
    value_list = pc.getRelatedValueList(bc)
    # Now the base category should be referred to by itself and this sub category
    self.assertEquals(len(value_list), 2)
    # This sub category should be referred to only by itself
    value_list = pc.getRelatedValueList(c)
    self.assertEquals(len(value_list), 1)

    #test _getDefaultRelatedProperty Accessor
    person = self.getPortal().person_module.newContent(id='person_test')
    org = self.getPortal().organisation_module.newContent(
                                  id='organisation_test',
                                  destination='person_module/person_test')
    get_transaction().commit()
    self.tic()
    self.assertEquals(person.getDefaultDestinationRelated(),
                                  'organisation_module/organisation_test' )

  def test_17_CategoriesAndDomainSelection(self, quiet=quiet,
      run=run_all_test):
    """ Tests Categories and Domain Selection """
    if not run: return
    if not quiet:
      message = 'Test Domain Selection and Categories'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)

    category_tool = self.getCategoryTool()
    base = category_tool.newContent(portal_type = 'Base Category',
                                   id='test_base_cat')
    test = base.newContent(portal_type = 'Category', id = 'test_cat')
    base.recursiveReindexObject()
    obj = self.getOrganisationModule().newContent(
          portal_type = 'Organisation')
    obj.setCategoryList(['test_base_cat/test_cat'])
    get_transaction().commit()
    self.tic()
    self.assert_(obj in [x.getObject() for x in test.getCategoryMemberValueList()])

  def test_18_CategoryIsMemberOfSelf(self, quiet=quiet, run=run_all_test):
    """
      A Category must be member of self. Otherwise, if for example
      a document has destination category C and we look for all documents
      which destination is part of C category, we will not find it.

      For example, the following commit was a mistake:
    http://svn.erp5.org/erp5/trunk/products/CMFCategory/CategoryTool.py?r1=8850&r2=9997
    """
    if not run: return
    if not quiet:
      message = 'Test if Category is Member of Self'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)

    portal = self.getPortal()
    europe = portal.portal_categories.resolveCategory('region/europe')
    self.failUnless('region/europe' in europe.getCategoryList())
    self.failUnless(europe.isMemberOf('region/europe'))

  def test_19_getCategoryList(self, quiet=quiet, run=run_all_test):
    """
    check that getCategoryList called on a category does not append self again
    and again
    """
    if not run: return
    if not quiet:
      message = 'Test getCategoryList on Category'
      ZopeTestCase._print('\n ' + message)
      LOG('Testing... ', 0, message)
    portal = self.getPortal()
    region_value = portal.portal_categories.resolveCategory('region/%s' % self.region1)
    category_list = region_value.getCategoryList()
    region_value.setCategoryList(category_list)
    self.assertEqual(category_list, region_value.getCategoryList())

  def test_19_CategoryMemberValueList(self, quiet=quiet, run=run_all_test):
    """Test strict_membership parameter to Category Member Value List """
    if not run : return
    if not quiet:
      message = 'Test strict_membership and Category Member Value List'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ',0,message)

    portal_categories = self.getCategoryTool()
    organisation = self.getOrganisationModule().newContent(
              portal_type='Organisation', region='west/france')

    get_transaction().commit()
    self.tic()

    self.assertEquals([x.getObject() for x in
                        portal_categories.getCategoryMemberValueList(
                          portal_categories.region.west.france,
                          base_category='region',
                          strict_membership=0,
                          portal_type='Organisation')], [organisation])

    self.assertEquals([x.getObject() for x in
                       portal_categories.getCategoryMemberValueList(
                          portal_categories.region.west.france,
                          base_category='region',
                          strict_membership=1,
                          portal_type='Organisation')], [organisation])

    self.assertEquals([x.getObject() for x in
                       portal_categories.getCategoryMemberValueList(
                          portal_categories.region.west,
                          base_category='region',
                          strict_membership=0,
                          portal_type='Organisation')], [organisation])

    self.assertEquals([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region.west,
                          base_category='region',
                          strict_membership=1,
                          portal_type='Organisation')], [])

  def test_20_CategoryChildTitleAndIdItemList(self, quiet=quiet,
                                              run=run_all_test):
    """Tests getCategoryChildTitleAndIdItemList."""
    if not run : return
    if not quiet:
      message = 'Test Category Child Title And Id Item List'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ',0,message)
    base_cat = self.getCategoryTool().newContent(portal_type='Base Category')
    cat = base_cat.newContent(portal_type='Category',
                              id='the_id', title='The Title')
    self.assertEquals([['', ''], ['The Title (the_id)', 'the_id']],
                       base_cat.getCategoryChildTitleAndIdItemList())

  def test_21_AcquiredPortalType(self, quiet=quiet, run=run_all_test):
    """Test if acquired_portal_type works correctly."""
    if not run : return
    if not quiet:
      message = 'Test Acquired Portal Type'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ',0,message)

    portal = self.getPortal()
    order = portal.sale_order_module[self.id1]
    packing_list = portal.sale_packing_list_module[self.id1]
    person = self.getPersonModule()[self.id1]

    person.setTitle('toto')
    self.assertEquals(person.getTitle(), 'toto')

    order.setDestinationAdministrationValue(person)
    self.assertEquals(order.getDestinationAdministrationPersonTitle(), 'toto')

    packing_list.setDestinationAdministrationValue(None)
    packing_list.setCausalityValue(None)
    self.assertEquals(packing_list.getDestinationAdministrationPersonTitle(), None)

    packing_list.setCausalityValue(order)
    self.assertEquals(packing_list.getDestinationAdministrationPersonTitle(), 'toto')

  def test_22_UserFriendlyException(self, quiet=quiet, run=run_all_test):
    """Test message raise if bad use of setter."""
    if not run : return
    if not quiet:
      message = 'Test User Friendly Exception'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ',0,message)
    person_module = self.getPersonModule()
    portal = self.getPortal()
    person_module = self.getPersonModule()
    if self.id1 not in person_module.objectIds():
      p1 = person_module.newContent(id=self.id1, title=self.id1)
    else:
      p1 = person_module._getOb(self.id1)
    organisation_module = self.getOrganisationModule()
    if self.id1 not in organisation_module.objectIds():
      o1 = organisation_module.newContent(id=self.id1)
    else:
      o1 = organisation_module._getOb(self.id1)

    try:
      p1.setCareerSubordination(o1)
    except Exception, e:
      self.failUnless(isinstance(e, TypeError))
      self.assertEqual(e.args[0], 'Category must be of string, tuple of '
                                  'string or list of string type.')

  def test_23_getCategoryChildValueList(self, quiet=quiet, run=run_all_test) :
    if not run: return
    if not quiet:
      message = 'Test getCategoryChildValueList and arguments'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)

    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='child_test')
    c1 = bc.newContent(portal_type='Category', id='1')
    c11 = c1.newContent(portal_type='Category', id='1.1')
    c111 = c11.newContent(portal_type='Category', id='1.1.1')
    c2 = bc.newContent(portal_type='Category', id='2')
    
    self.assertSameSet(bc.getCategoryChildValueList(), (c1, c11, c111, c2))
    self.assertSameSet(c1.getCategoryChildValueList(), (c11, c111,))
    
    # recursive
    self.assertSameSet(bc.getCategoryChildValueList(recursive=0), (c1, c2))
    self.assertSameSet(c1.getCategoryChildValueList(recursive=0), (c11, ))

    # only leaves
    self.assertSameSet(bc.getCategoryChildValueList(include_if_child=0),
                                                    (c111, c2))
    self.assertSameSet(c1.getCategoryChildValueList(include_if_child=0),
                                                    (c111, ))
    # including self
    self.assertSameSet(bc.getCategoryChildValueList(is_self_excluded=0),
                                                    (bc, c1, c11, c111, c2))
    self.assertSameSet(c1.getCategoryChildValueList(is_self_excluded=0),
                                                    (c1, c11, c111))

  def test_24_getCategoryChildValueListLocalSortMethod(self,
                              quiet=quiet, run=run_all_test) :
    if not run: return
    if not quiet:
      message = 'Test getCategoryChildValueList local sort method'
      ZopeTestCase._print('\n '+message)
      LOG('Testing... ', 0, message)

    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='child_test')
    c1 = bc.newContent(portal_type='Category', id='1', int_index=10, title='C')
    c11 = c1.newContent(portal_type='Category', id='1.1', int_index=5, title='X')
    c111 = c11.newContent(portal_type='Category', id='1.1.1',
                          int_index=2, title='C')
    c12 = c1.newContent(portal_type='Category', id='1.2', int_index=3, title='Z')
    c2 = bc.newContent(portal_type='Category', id='2', int_index=30, title='B')
    c3 = bc.newContent(portal_type='Category', id='3', int_index=20, title='A')
    
    # the default ordering is preorder:
    self.assertEquals(list(bc.getCategoryChildValueList()),
                      [c1, c11, c111, c12, c2, c3])
    self.assertEquals(list(c1.getCategoryChildValueList()), [c11, c111, c12])
    
    # but this order can be controlled for categories of the same depth, ie. we
    # can sort each level independantly (this is different from sort_on /
    # sort_order which sort the whole list regardless of the original
    # structure).

    # This can be done either with a function (like cmp argument to python
    # list sort)
    def sort_func(a, b):
      return cmp(a.getTitle(), b.getTitle())
    # here c1, c2, c3 are sorted by their titles
    self.assertEquals(list(bc.getCategoryChildValueList(
                                        local_sort_method=sort_func)),
                      [c3, c2, c1, c11, c111, c12])
    # here c11 & c12 are sorted by their titles
    self.assertEquals(list(c1.getCategoryChildValueList(
                              local_sort_method=sort_func)), [c11, c111, c12])

    # This can also be done with a local_sort_id, then objects are sorted by
    # comparing this 'sort_id' property (using getProperty())
    # here c1, c2, c3 are sorted by their int_index
    self.assertEquals(list(bc.getCategoryChildValueList(
                                        local_sort_id='int_index')),
                      [c1, c12, c11, c111, c3, c2])
    # here c11 & c12 are sorted by their titles
    self.assertEquals(list(c1.getCategoryChildValueList(
                              local_sort_id='int_index')), [c12, c11, c111])

  
  def test_25_getCategoryChildItemList_base_parameter(self):
    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='foo')
    c1 = bc.newContent(portal_type='Category', id='1', title='C')
    
    self.assertEquals([['', ''], ['C', '1']],
                      bc.getCategoryChildTitleItemList())
    self.assertEquals([['', ''], ['C', '1']],
                      bc.getCategoryChildTitleItemList(base=0))
    self.assertEquals([['', ''], ['C', 'foo/1']],
                      bc.getCategoryChildTitleItemList(base=1))
    self.assertEquals([['', ''], ['C', 'bar/foo/1']],
                      bc.getCategoryChildTitleItemList(base='bar'))

    
  def test_getSingleCategoryAcquiredMembershipList(self):
    pc = self.getCategoriesTool()
    obj = self.portal.person_module.newContent(portal_type='Person')
    region_url = self.region1
    obj.setRegion(region_url)

    self.assertEquals([region_url],
          pc.getSingleCategoryMembershipList(obj, 'region'))

    self.assertEquals([region_url],
          pc.getSingleCategoryMembershipList(obj, 'region',
                        portal_type='Category'))
    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'region',
                        portal_type='Organisation'))

    self.assertEquals(['region/%s' % region_url],
          pc.getSingleCategoryMembershipList(obj, 'region', base=1))

    self.assertEquals([region_url],
          pc.getSingleCategoryMembershipList(obj, 'region',
                                checked_permission='View'))
    noSecurityManager()
    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'region',
                                checked_permission='Manage portal'))


  def test_getSingleCategoryAcquiredMembershipListOnParent(self):
    pc = self.getCategoriesTool()
    obj = self.portal.person_module.newContent(portal_type='Person')
    parent_url = self.portal.person_module.getRelativeUrl()

    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'parent'))

    self.assertEquals([parent_url],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                        portal_type='Person Module'))

    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                        portal_type='Organisation'))

    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'parent', base=1))

    self.assertEquals(['parent/%s' % parent_url],
          pc.getSingleCategoryMembershipList(obj, 'parent', base=1,
                        portal_type='Person Module'))

    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='View'))

    self.assertEquals([parent_url],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='View',
                                portal_type='Person Module'))

    noSecurityManager()
    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='Manage portal'))
    self.assertEquals([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='Manage portal',
                                portal_type='Person Module'))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCMFCategory))
  return suite

