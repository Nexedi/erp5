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

from collections import deque
import unittest

from Acquisition import aq_base
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.CMFCategory.Category import NBSP_UTF8
from Testing.ZopeTestCase.PortalTestCase import PortalTestCase
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager

class TestCMFCategory(ERP5TypeTestCase):

  # Different variables used for this test
  id1 = '1'
  id2 = '2'
  region1 = 'europe/west/france'
  region2 = 'europe/west/germany'
  region_list = [region1, region2]

  category_dict = dict(
    region = dict(
      acquisition_base_category_list=('subordination','parent'),
      acquisition_portal_type_list="python: ['Address', 'Organisation', 'Person']",
      acquisition_mask_value=1,
      acquisition_object_id_list=['default_address'],
      contents=('europe', ('west', ('france', 'germany'))),
      ),
    subordination = dict(
      acquisition_portal_type_list="python: ['Career', 'Organisation']",
      acquisition_object_id_list=['default_career'],
      ),
    gender = dict(
      fallback_base_category_list=['subordination'],
      ),
    resource = dict(
      ),
    test0 = dict(
      ),
    test1 = dict(
      contents=('a', ('ab', 'ac', ('acd',))),
      ),
    )

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
    return ('erp5_base', 'erp5_pdm', 'erp5_trade')

  def getCategoriesTool(self):
    return getattr(self.portal, 'portal_categories', None)

  def test_00_HasEverything(self):
    self.assertNotEquals(self.getCategoriesTool(), None)
    self.assertNotEquals(self.getPersonModule(), None)
    self.assertNotEquals(self.getOrganisationModule(), None)

  def afterSetUp(self):
    self.login()
    portal = self.portal
    self.validateRules()

    portal_categories = self.getCategoriesTool()
    for name, kw in self.category_dict.iteritems():
      try:
        bc = portal_categories[name]
      except KeyError:
        bc = portal_categories.newContent(name)
      edit_kw = dict(
        acquisition_copy_value=0,
        acquisition_append_value=0,
        acquisition_mask_value=0,
        acquisition_portal_type_list="python: []",
        related_locally_indexed=0)
      edit_kw.update(kw)
      queue = deque(((bc, edit_kw.pop('contents', ())),))
      bc.edit(**edit_kw)
      while queue:
        parent, contents = queue.popleft()
        for x in contents:
          if type(x) is str:
            try:
              category = parent[x]
            except KeyError:
              category = parent.newContent(x)
          else:
            queue.append((category, x))

    # This test creates Person inside Person and Organisation inside
    # Organisation, so we modify type informations to allow anything inside
    # Person and Organisation (we'll cleanup on teardown).
    self._original_categories = {}
    for portal_type, categories in (
        ('Person', []),
        ('Organisation', ['destination', 'resource'])):
      ti = self.getTypesTool().getTypeInfo(portal_type)
      ti.filter_content_types = 0
      self._original_categories[portal_type] = x = ti.getTypeBaseCategoryList()
      x += 'test0', 'test1'
      ti._setTypeBaseCategoryList(x + categories)

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

  def beforeTearDown(self):
    """Clean up."""
    # type informations
    for portal_type, categories in self._original_categories.iteritems():
      ti = self.getTypesTool().getTypeInfo(portal_type)
      ti.filter_content_types = 1
      ti._setTypeBaseCategoryList(categories)

  def login(self):
    uf = self.portal.acl_users
    uf._doAddUser('seb', '', ['Manager'], [])
    user = uf.getUserById('seb').__of__(uf)
    newSecurityManager(None, user)

  def test_01_SingleCategory(self):
    # Test if a single category is working
    o1 = self.getOrganisationModule()._getOb(self.id1)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region1)
    self.assertEqual(p1.getRegion(), self.region1)
    self.assertEqual(p1.getRegion('foo'), self.region1)
    self.assertEqual(p1.getDefaultRegion(), self.region1)
    self.assertEqual(p1.getDefaultRegion('foo'), self.region1)
    self.assertEqual(p1.getRegionList(), [self.region1])
    self.assertEqual(p1.getRegionList(['foo']), [self.region1])

  def test_02_MultipleCategory(self):
    # Test if multiple categories are working
    region_value_list = [self.portal.portal_categories.resolveCategory('region/%s' % self.region1),
                         self.portal.portal_categories.resolveCategory('region/%s' % self.region2)]
    self.assertNotEqual(None,region_value_list[0])
    self.assertNotEqual(None,region_value_list[1])
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegion(),self.region1)
    self.assertEqual(p1.getDefaultRegion(),self.region1)
    self.assertEqual(p1.getRegionList(),self.region_list)

    p1.setRegion(self.region1)
    self.assertEqual(p1.getRegion(), self.region1)
    region_list = p1.getRegionList()
    p1.setRegionList(region_list)
    self.assertEqual(p1.getRegion(), self.region1)
    region_list = [p1.getRegion()]
    p1.setRegionList(region_list)
    self.assertEqual(p1.getRegion(), self.region1)
    p1.setRegion(None)
    self.assertEqual(p1.getRegion(), None)
    region_list = p1.getRegionList()
    p1.setRegionList(region_list)
    self.assertEqual(p1.getRegion(), None)
    region_list = [p1.getRegion()]
    p1.setRegionList(region_list)
    self.assertEqual(p1.getRegion(), None)

  def test_03_CategoryValue(self):
    # Test if we can get categories values
    region_value = self.portal.portal_categories.resolveCategory('region/%s' % self.region1)
    self.assertNotEqual(None,region_value)
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region_list)
    self.assertEqual(p1.getRegionValue(),region_value)

  def test_isMemberOf(self):
    region_path = 'region/%s' % self.region1
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(None)
    self.assertFalse(p1.isMemberOf(region_path))
    p1.setRegion(self.region1)
    self.assertTrue(p1.isMemberOf(region_path))

  def test_isAcquiredMemberOf(self):
    region_path = 'region/%s' % self.region1
    p1 = self.getPersonModule()._getOb(self.id1)
    sub_person = p1._getOb(self.id1)
    p1.setRegion(None)
    self.assertFalse(p1.isAcquiredMemberOf(region_path))
    self.assertFalse(sub_person.isAcquiredMemberOf(region_path))
    p1.setRegion(self.region1)
    self.assertTrue(p1.isAcquiredMemberOf(region_path))
    self.assertTrue(sub_person.isAcquiredMemberOf(region_path))

  def test_04_ReturnNone(self):
    # Test if we getCategory return None if the cat is '' or None
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(None)
    self.assertEqual(p1.getRegion(),None)
    p1.setRegion('')
    self.assertEqual(p1.getRegion(),None)

  def test_05_SingleAcquisition(self):
    # Test if the acquisition for a single value is working
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
    self.assertTrue(p1.isMemberOf('region/%s' % self.region1))

  def test_06_ListAcquisition(self):
    # Test if the acquisition for a single value is working
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
    self.assertTrue(p1.isMemberOf('region/%s' % self.region1))

  def test_07_SubordinationValue(self):
    # Test if an infinite loop of the acquisition for a single value is working
    p1 = self.getPersonModule()._getOb(self.id1)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1.setSubordinationValue(o1)
    p1.setRegion(None)
    self.assertEqual(p1.getSubordinationValue(),o1)
    self.assertEqual(p1.getDefaultSubordinationValue(),o1)
    self.assertEqual(p1.getSubordinationValueList(),[o1])

  def test_08_SubordinationMultipleValue(self):
    # Test if an infinite loop of the acquisition for a single value is working
    p1 = self.getPersonModule()._getOb(self.id1)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    o2 = self.getOrganisationModule()._getOb(self.id2)
    subordination_value_list = [o1,o2]
    p1.setSubordinationValueList(subordination_value_list)
    p1.setRegion(None)
    self.assertEqual(p1.getSubordinationValue(),o1)
    self.assertEqual(p1.getDefaultSubordinationValue(),o1)
    self.assertEqual(p1.getSubordinationValueList(),subordination_value_list)

  def test_09_GetCategoryParentUidList(self):
    # Test if an infinite loop of the acquisition for a single value is working
    portal_categories = self.getCategoriesTool()
    getCategoryParentUidList = portal_categories.getCategoryParentUidList
    basecat = portal_categories.newContent(portal_type='Base Category', id='basecat')
    basecat2 = portal_categories.newContent(portal_type='Base Category', id='basecat2')
    cat1 = basecat.newContent(portal_type='Category', id='cat1')
    cat2 = cat1.newContent(portal_type='Category', id='cat2')
    cat22 = cat2.newContent(portal_type='Category', id='cat2')
    cat3 = cat1.newContent(portal_type='Category', id='cat3')
    module = self.getPersonModule()
    person = module.newContent(portal_type='Person')
    address = person.newContent(portal_type='Address')
    # Non-strict, implicit base category
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=cat2.getRelativeUrl(),
      ),
      [
        (cat2.getUid(), basecat.getUid(), 1),
        (cat1.getUid(), basecat.getUid(), 0),
      ],
    )
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=cat22.getRelativeUrl(),
      ),
      [
        (cat22.getUid(), basecat.getUid(), 1),
        (cat2.getUid(), basecat.getUid(), 0),
        (cat1.getUid(), basecat.getUid(), 0),
      ],
    )
    # Non-canonical path
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=cat2.getRelativeUrl() + '/' + cat3.getId(),
      ),
      [
        (cat3.getUid(), basecat.getUid(), 1),
        (cat2.getUid(), basecat.getUid(), 0),
        (cat1.getUid(), basecat.getUid(), 0),
      ],
    )
    # Strict, implicit base category
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=cat2.getRelativeUrl(),
        strict=True,
      ),
      [
        (cat2.getUid(), basecat.getUid(), 1),
      ],
    )
    # Non-strict, explicit base category
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=cat2.getRelativeUrl(),
        base_category=basecat2.getId(),
      ),
      [
        (cat2.getUid(), basecat2.getUid(), 1),
        (cat1.getUid(), basecat2.getUid(), 0),
        (basecat.getUid(), basecat2.getUid(), 0),
      ],
    )
    # Strict, explicit base category
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=cat2.getRelativeUrl(),
        base_category=basecat2.getId(),
        strict=True,
      ),
      [
        (cat2.getUid(), basecat2.getUid(), 1),
      ],
    )
    # Non-strict with a non-category relation: only strict relation uid.
    # Note: not providing base_category is undefined behaviour.
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=person.getRelativeUrl(),
        base_category=basecat.getId(),
      ),
      [
        (person.getUid(), basecat.getUid(), 1),
      ],
    )
    # ... even on a subobject
    self.assertItemsEqual(
      getCategoryParentUidList(
        relative_url=address.getRelativeUrl(),
        base_category=basecat.getId(),
      ),
      [
        (address.getUid(), basecat.getUid(), 1),
      ],
    )

  def test_10_FallBackBaseCategory(self):
    # Test if we can use an alternative base category
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
    self.assertTrue(p1.isMemberOf('gender/organisation_module/%s' % self.id1))

  def test_11_ParentAcquisition(self):
    # Test if we can use an alternative base category
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
    self.assertTrue(p1.isMemberOf('region/%s' % self.region1))
    self.assertTrue(sub_person.isMemberOf('region/%s' % self.region1))

  def test_parentAcquisitionIsMemberOfWithDifferentCategories(self):
    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion(self.region1)
    sub_person = p1._getOb(self.id1)
    self.assertTrue(p1.isMemberOf('region/%s' % self.region1))
    sub_person.setRegion(self.region2)
    self.assertTrue(sub_person.isMemberOf('region/%s' % self.region2))

  def test_12_GetRelatedValueAndValueList(self):
    # Test if an infinite loop of the acquisition for a single value is working
    # Typical error results from bad brain (do not copy, use aliases for zsqlbrain.py)
    p1 = self.getPersonModule()._getOb(self.id1)
    p2 = self.getPersonModule()._getOb(self.id2)
    o1 = self.getOrganisationModule()._getOb(self.id1)
    p1.setGenderValue(o1)
    self.tic()# This is required

    self.assertEqual(p1.getGenderValue(),o1)
    self.assertEqual(o1.getGenderRelatedValueList(),[p1])
    p2.setGenderValue(o1) # reindex implicit
    self.tic()

    self.assertEqual(len(o1.getGenderRelatedValueList()),2)

  def test_13_RenameCategory(self):
    france = self.portal.portal_categories.resolveCategory(
                                            'region/europe/west/france')
    self.assertNotEqual(france, None)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion('europe/west/france')
    self.tic()

    west = self.portal.portal_categories.resolveCategory('region/europe/west')
    west.setId("ouest")
    self.tic()

    self.assertEqual(west,
      self.portal.portal_categories.resolveCategory('region/europe/ouest'))
    # documents using this category are updated
    self.assertEqual(p1.getRegion(), 'europe/ouest/france')
    self.assertTrue(p1 in west.getRegionRelatedValueList())
    # category itself is also updated
    self.assertEqual(['region/europe/ouest'], west.getCategoryList())
    self.assertEqual(['region/europe/ouest/france'], west.france.getCategoryList())

  def test_13b_RenameCategoryUsingCutAndPaste(self):
    france = self.portal.portal_categories.resolveCategory(
                                            'region/europe/west/france')
    self.assertNotEqual(france, None)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion('europe/west/france')
    self.tic()

    europe = self.portal.portal_categories.resolveCategory('region/europe')
    west = europe.west
    cb_data = europe.manage_cutObjects(['west'])
    self.portal.portal_categories.region.manage_pasteObjects(cb_data)
    self.tic()

    self.assertEqual(west,
      self.portal.portal_categories.resolveCategory('region/west'))
    # documents using this category are updated
    self.assertEqual(p1.getRegion(), 'west/france')
    self.assertTrue(p1 in west.getRegionRelatedValueList())
    # category itself is also updated ( but we need to get it in its new acquisition context )
    self.assertEqual(['region/west'], self.portal.portal_categories.region.west.getCategoryList())

  def test_13c_RenameCategoryUsingCutAndPasteButNotCopy(self):
    france = self.portal.portal_categories.resolveCategory(
                                    'region/europe/west/france')
    self.assertNotEqual(france, None)

    p1 = self.getPersonModule()._getOb(self.id1)
    p1.setRegion('europe/west/france')
    self.tic()

    europe = self.portal.portal_categories.resolveCategory('region/europe')
    west = europe.west
    cb_data = europe.manage_copyObjects(['west'])
    self.portal.portal_categories.region.manage_pasteObjects(cb_data)
    self.tic()

    self.assertEqual(west,
      self.portal.portal_categories.resolveCategory('region/europe/west'))
    self.assertEqual(p1.getRegion(), 'europe/west/france')
    # documents using the category are not member of the copy
    self.assertTrue('west/france' not in p1.getRegionList())
    self.assertTrue(p1 in west.getRegionRelatedValueList())

  def test_14_MultiplePortalTypes(self):
    """ Checks that categories support different value per portal_type,
        like a colored graph on portal_type"""
    folder = self.getOrganisationModule()

    org_a = folder.newContent(portal_type='Organisation', id="org_a")
    org_b = folder.newContent(portal_type='Organisation', id="org_b")

    org_a.setDestinationValue(org_b)
    self.assertEqual(org_a.getDestinationValue(), org_b)

    pers_a = self.getPersonModule().newContent(
                  portal_type='Person', id='pers_a')

    for loop in range(3):
      org_a.setDestinationValue(pers_a, portal_type='Person')
      self.assertEqual(
          org_a.getDestinationValue(portal_type='Person'), pers_a)
      self.assertEqual(
          org_a.getDestinationValue(portal_type='Organisation'), org_b)
      self.assertEqual(len(org_a.getDestinationValueList()), 2)

      org_a.setDestinationValue(org_b, portal_type='Organisation')
      self.assertEqual(
          org_a.getDestinationValue(portal_type='Person'), pers_a)
      self.assertEqual(
          org_a.getDestinationValue(portal_type='Organisation'), org_b)
      self.assertEqual(len(org_a.getDestinationValueList()), 2)

  def test_15_SortChildValues(self):
    """ Checks on sorting child categories"""
    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='sort_test')
    self.assertTrue(bc is not None)
    bc.newContent(portal_type='Category', id='1', title='a', int_index=3)
    bc.newContent(portal_type='Category', id='2', title='b', int_index=1)
    bc.newContent(portal_type='Category', id='3', title='c', int_index=1)

    # simple sorting
    category_list = bc.getCategoryChildValueList(sort_on='title')
    self.assertEqual(len(category_list), 3)
    self.assertEqual(category_list[0].getId(), '1')
    self.assertEqual(category_list[1].getId(), '2')
    self.assertEqual(category_list[2].getId(), '3')

    # reverse sorting
    category_list = bc.getCategoryChildValueList(sort_on='title', sort_order='reverse')
    self.assertEqual(len(category_list), 3)
    self.assertEqual(category_list[0].getId(), '3')
    self.assertEqual(category_list[1].getId(), '2')
    self.assertEqual(category_list[2].getId(), '1')

    # another reverse sorting
    category_list = bc.getCategoryChildValueList(sort_on=(('title', 'reverse'),))
    self.assertEqual(len(category_list), 3)
    self.assertEqual(category_list[0].getId(), '3')
    self.assertEqual(category_list[1].getId(), '2')
    self.assertEqual(category_list[2].getId(), '1')

    # multiple sort parameters
    category_list = bc.getCategoryChildValueList(sort_on=('int_index', 'title'))
    self.assertEqual(len(category_list), 3)
    self.assertEqual(category_list[0].getId(), '2')
    self.assertEqual(category_list[1].getId(), '3')
    self.assertEqual(category_list[2].getId(), '1')

    # another multiple sort parameters
    category_list = bc.getCategoryChildValueList(sort_on=(('int_index', 'reverse'), 'title'))
    self.assertEqual(len(category_list), 3)
    self.assertEqual(category_list[0].getId(), '1')
    self.assertEqual(category_list[1].getId(), '2')
    self.assertEqual(category_list[2].getId(), '3')

  def test_16_GetRelatedValues(self):
    """ Checks on getting related values"""
    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='related_value_test')
    self.tic()
    self.assertItemsEqual(pc.getRelatedValueList(bc), [bc])

    c1 = bc.newContent(portal_type='Category', id='1')
    self.tic()
    self.assertItemsEqual(pc.getRelatedValueList(bc), [bc])
    self.assertItemsEqual(pc.getRelatedValueList(c1), [c1])

    c11 = c1.newContent(portal_type='Category', id='1')
    self.tic()
    self.assertItemsEqual(pc.getRelatedValueList(bc), [bc])
    self.assertItemsEqual(pc.getRelatedValueList(c1), [c1, c11])
    self.assertItemsEqual(pc.getRelatedValueList(c11), [c11])

    #test _getDefaultRelatedProperty Accessor
    person = self.portal.person_module.newContent(id='person_test')
    org = self.portal.organisation_module.newContent(
                                  id='organisation_test',
                                  destination='person_module/person_test')
    self.tic()
    self.assertEqual(person.getDefaultDestinationRelated(),
                                  'organisation_module/organisation_test' )

  def test_17_CategoriesAndDomainSelection(self):
    """ Tests Categories and Domain Selection """
    category_tool = self.getCategoryTool()
    base = category_tool.newContent(portal_type='Base Category',
                                   id='test_base_cat')
    test = base.newContent(portal_type='Category', id='test_cat')
    base.recursiveReindexObject()
    obj = self.getOrganisationModule().newContent(
          portal_type = 'Organisation')
    obj.setCategoryList(['test_base_cat/test_cat'])
    self.tic()
    self.assert_(obj in [x.getObject() for x in test.getCategoryMemberValueList()])

  def test_18_CategoryIsMemberOfSelf(self):
    """
      A Category must be member of self. Otherwise, if for example
      a document has destination category C and we look for all documents
      which destination is part of C category, we will not find it.

      ( XXX not sure of this example, I guess it works because non strict
      membership is indexed -jerome )

    """
    europe = self.portal.portal_categories.resolveCategory('region/europe')
    self.assertIn('region/europe', europe.getCategoryList())
    self.assertTrue(europe.isMemberOf('region/europe'))

    # this membership is not saved in .categories
    self.assertNotIn('region/europe', getattr(aq_base(europe), 'categories', ()))

    # even if we set explicitly
    europe.setCategoryList(europe.getCategoryList())
    self.assertNotIn('region/europe', getattr(aq_base(europe), 'categories', ()))

    # or if we set other categories
    europe.setCategoryList(['subordination/person_module'])
    self.assertItemsEqual(
            ['region/europe', 'subordination/person_module'],
            europe.getCategoryList())
    self.assertEqual(
            ('subordination/person_module',),
            getattr(aq_base(europe), 'categories', ()))

  def test_19_CategoryMemberValueList(self):
    """Test strict_membership parameter to Category Member Value List """
    portal_categories = self.getCategoryTool()
    organisation = self.getOrganisationModule().newContent(
              test0='region/europe', test1='region',
              portal_type='Organisation', region='europe/west/france')

    self.tic()

    self.assertEqual([x.getObject() for x in
                        portal_categories.getCategoryMemberValueList(
                          portal_categories.region.europe.west.france,
                          base_category='region',
                          strict_membership=0,
                          portal_type='Organisation')], [organisation])
    self.assertEqual([x.getObject() for x in
                       portal_categories.getCategoryMemberValueList(
                          portal_categories.region.europe.west.france,
                          base_category='region',
                          strict_membership=1,
                          portal_type='Organisation')], [organisation])

    self.assertEqual([x.getObject() for x in
                       portal_categories.getCategoryMemberValueList(
                          portal_categories.region.europe.west,
                          base_category='region',
                          strict_membership=0,
                          portal_type='Organisation')], [organisation])
    self.assertEqual([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region.europe.west,
                          base_category='region',
                          strict_membership=1,
                          portal_type='Organisation')], [])

    self.assertEqual([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region,
                          base_category='region',
                          portal_type='Organisation')], [organisation])

    self.assertEqual([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region,
                          base_category='test0',
                          strict_membership=0,
                          portal_type='Organisation')], [organisation])
    self.assertEqual([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region,
                          base_category='test0',
                          strict_membership=1,
                          portal_type='Organisation')], [])

    self.assertEqual([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region,
                          base_category='test1',
                          strict_membership=0,
                          portal_type='Organisation')], [organisation])
    self.assertEqual([x.getObject() for x in
                      portal_categories.getCategoryMemberValueList(
                          portal_categories.region,
                          base_category='test1',
                          strict_membership=1,
                          portal_type='Organisation')], [organisation])

  def test_20_CategoryChildIndentedTitle(self):
    base_cat = self.getCategoryTool().newContent(portal_type='Base Category')
    cat = base_cat.newContent(portal_type='Category',
                              id='the_id', title='The Title')
    sub_cat = cat.newContent(portal_type='Category',
                             id='the_sub_id', title='The Sub Title')
    whitespace_number = self.portal.portal_preferences.getPreferredWhitespaceNumberForChildItemIndentation()
    self.assertEqual(NBSP_UTF8 * whitespace_number + 'The Sub Title', sub_cat.getIndentedTitle())

  def test_20_CategoryChildTitleAndIdItemList(self):
    """Tests getCategoryChildTitleAndIdItemList."""
    base_cat = self.getCategoryTool().newContent(portal_type='Base Category')
    cat = base_cat.newContent(portal_type='Category',
                              id='the_id', title='The Title')
    self.assertEqual([['', ''], ['The Title (the_id)', 'the_id']],
                       base_cat.getCategoryChildTitleAndIdItemList())

  def test_20_CategoryChildCompactTitleItemList(self):
    # Tests getCategoryChildCompactTitleItemList
    base_cat = self.getCategoryTool().newContent(portal_type='Base Category')
    cat = base_cat.newContent(portal_type='Category',
          id='the_id', title='The Title', short_title='The T.')
    self.assertEqual([['', ''], ['The T.', 'the_id']],
                       base_cat.getCategoryChildCompactTitleItemList())
    self.assertEqual([['', ''], ['The T.', 'the_id']],
             base_cat.getCategoryChildTranslatedCompactTitleItemList())

  def test_21_AcquiredPortalType(self):
    """Test if acquired_portal_type works correctly."""

    order = self.portal.sale_order_module[self.id1]
    packing_list = self.portal.sale_packing_list_module[self.id1]
    person = self.getPersonModule()[self.id1]

    person.setTitle('toto')
    self.assertEqual(person.getTitle(), 'toto')

    order.setDestinationAdministrationValue(person)
    self.assertEqual(order.getDestinationAdministrationPersonTitle(), 'toto')

    packing_list.setDestinationAdministrationValue(None)
    packing_list.setOrderValue(None)
    self.assertEqual(packing_list.getDestinationAdministrationPersonTitle(), None)

    packing_list.setOrderValue(order)
    self.assertEqual(packing_list.getDestinationAdministrationPersonTitle(), 'toto')

  def test_22_UserFriendlyException(self):
    """Test message raise if bad use of setter."""
    person_module = self.getPersonModule()
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
      self.assertTrue(isinstance(e, TypeError))
      self.assertEqual(e.args[0], 'CategoryTool.setCategoryMembership '
                                  'only takes string(s) as value')

  def test_23_getCategoryChildValueList(self):
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

  def test_24_getCategoryChildValueListLocalSortMethod(self):
    '''Test getCategoryChildValueList local sort method'''
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
    self.assertEqual(list(bc.getCategoryChildValueList()),
                      [c1, c11, c111, c12, c2, c3])
    self.assertEqual(list(c1.getCategoryChildValueList()), [c11, c111, c12])

    # but this order can be controlled for categories of the same depth, ie. we
    # can sort each level independantly (this is different from sort_on /
    # sort_order which sort the whole list regardless of the original
    # structure).

    # This can be done either with a function (like cmp argument to python
    # list sort)
    def sort_func(a, b):
      return cmp(a.getTitle(), b.getTitle())
    # here c1, c2, c3 are sorted by their titles
    self.assertEqual(list(bc.getCategoryChildValueList(
                                        local_sort_method=sort_func)),
                      [c3, c2, c1, c11, c111, c12])
    # here c11 & c12 are sorted by their titles
    self.assertEqual(list(c1.getCategoryChildValueList(
                              local_sort_method=sort_func)), [c11, c111, c12])

    # This can also be done with a local_sort_id, then objects are sorted by
    # comparing this 'sort_id' property (using getProperty())
    # here c1, c2, c3 are sorted by their int_index
    self.assertEqual(list(bc.getCategoryChildValueList(
                                        local_sort_id='int_index')),
                      [c1, c12, c11, c111, c3, c2])
    # here c11 & c12 are sorted by their titles
    self.assertEqual(list(c1.getCategoryChildValueList(
                              local_sort_id='int_index')), [c12, c11, c111])

    # local_sort_id can be a list, in this case document are sorted with the
    # first sort_id in the list, then the second, and so on.

    # When we use those category properties:
    #        int_index     title
    #   c1                   C
    #   c2                   B
    #   c3      1            A
    c1.setIntIndex(None)
    c2.setIntIndex(None)
    # and we sort on int_index then title, we should have this order:
    self.assertEqual(list(bc.getCategoryChildValueList(
                          local_sort_id=['int_index', 'title'])),
                      [c2, c1, c12, c11, c111, c3])


  def test_25_getCategoryChildItemList_base_parameter(self):
    pc = self.getCategoriesTool()
    bc = pc.newContent(portal_type='Base Category', id='foo')
    c1 = bc.newContent(portal_type='Category', id='1', title='C')

    self.assertEqual([['', ''], ['C', '1']],
                      bc.getCategoryChildTitleItemList())
    self.assertEqual([['', ''], ['C', '1']],
                      bc.getCategoryChildTitleItemList(base=0))
    self.assertEqual([['', ''], ['C', 'foo/1']],
                      bc.getCategoryChildTitleItemList(base=1))
    self.assertEqual([['', ''], ['C', 'bar/foo/1']],
                      bc.getCategoryChildTitleItemList(base='bar'))


  def test_getSingleCategoryAcquiredMembershipList(self):
    pc = self.getCategoriesTool()
    obj = self.portal.person_module.newContent(portal_type='Person')
    region_url = self.region1
    obj.setRegion(region_url)

    self.assertEqual([region_url],
          pc.getSingleCategoryMembershipList(obj, 'region'))

    self.assertEqual([region_url],
          pc.getSingleCategoryMembershipList(obj, 'region',
                        portal_type='Category'))
    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'region',
                        portal_type='Organisation'))

    self.assertEqual(['region/%s' % region_url],
          pc.getSingleCategoryMembershipList(obj, 'region', base=1))

    self.assertEqual([region_url],
          pc.getSingleCategoryMembershipList(obj, 'region',
                                checked_permission='View'))
    noSecurityManager()
    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'region',
                                checked_permission='Manage portal'))


  def test_getSingleCategoryAcquiredMembershipListOnParent(self):
    pc = self.getCategoriesTool()
    obj = self.portal.person_module.newContent(portal_type='Person')
    parent = self.portal.person_module
    # due to using getAcquiredPropertyList() for temp object, the change
    # in r.22671 is required, and getSingleCategoryMembershipList()
    # returns parent object itself instead of its relative url.
    #parent_url = self.portal.person_module.getRelativeUrl()
    parent_url = parent.getRelativeUrl()

    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'parent'))

    #self.assertEqual([parent_url],
    self.assertEqual([parent],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                        portal_type='Person Module'))

    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                        portal_type='Organisation'))

    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'parent', base=1))

    #self.assertEqual(['parent/%s' % parent_url],
    self.assertEqual([parent],
          pc.getSingleCategoryMembershipList(obj, 'parent', base=1,
                        portal_type='Person Module'))

    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='View'))

    #self.assertEqual([parent_url],
    self.assertEqual([parent],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='View',
                                portal_type='Person Module'))

    noSecurityManager()
    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='Manage portal'))
    self.assertEqual([],
          pc.getSingleCategoryMembershipList(obj, 'parent',
                                checked_permission='Manage portal',
                                portal_type='Person Module'))

  def clearCategoryCache(self):
    """ Clear cache to remove old categories values. It would be much
        better to use cache cookie and interaction when category is modified. """
    self.portal.portal_caches.clearCache(
      cache_factory_list=('erp5_ui_long',))

  def _testGetCategoryChildItemListWithCheckedPermission(self, cache=None):
    uf = self.getPortal().acl_users
    uf._doAddUser('alice', '', ['Member', 'Manager', 'Assignor'], [])
    uf._doAddUser('bob', '', ['Member'], [])
    pc = self.getCategoriesTool()

    bc_id = 'barfoo'
    bc = pc.newContent(portal_type='Base Category', id=bc_id)
    a = bc.newContent(portal_type='Category', id='1', title='A')
    b = bc.newContent(portal_type='Category', id='2', title='B')
    b1 = b.newContent(portal_type='Category', id='21', title='B1')

    checked_permission = 'View'

    self.assertEqual(
      [['', ''], ['A', '1'], ['B', '2'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(cache=cache))
    self.assertEqual(
      [['', ''], ['A', '1'], ['B', '2'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       cache=cache))
    self.assertEqual(
      [['', ''], ['A', '1'], ['B', '2'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       current_category_list=['barfoo/2/21', 'barfoo/1'],
                                       cache=cache))

    b.manage_permission(checked_permission, roles=[], acquire=0)
    self.clearCategoryCache()

    self.assertEqual(
      3, len(bc.getCategoryChildValueList(cache=cache)))
    self.assertEqual(
      1,
      len(bc.getCategoryChildValueList(checked_permission=checked_permission,
                                       cache=cache)))

    self.assertEqual(
      ['%s/1' % bc_id, '%s/2' % bc_id, '%s/2/21' % bc_id],
      bc.getCategoryChildRelativeUrlList())
    self.assertEqual(
      ['%s/1' % bc_id],
      bc.getCategoryChildRelativeUrlList(checked_permission=checked_permission))

    self.assertEqual(
      [['', ''], ['A', '1'], ['B', '2'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(cache=cache))
    self.assertEqual(
      [['', ''], ['A', '1']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       cache=cache))
    # Verify that current_category_list parameter allows to display again
    # hidden values
    self.assertEqual(
      [['', ''], ['A', '1'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       current_category_list=['barfoo/2/21'],
                                       cache=cache))

    a.manage_permission(checked_permission, roles=[], acquire=0)
    self.clearCategoryCache()
    self.assertEqual(
      [['', '']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       cache=cache))
    self.assertEqual(
      [['', ''], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       current_category_list=['barfoo/2/21'],
                                       cache=cache))
    self.assertEqual(
      [['', ''], ['A', '1'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,
                                       current_category_list=['barfoo/1', 'barfoo/2/21'],
                                       cache=cache))

    # Result can be different depending on user, so make sure result is correct
    # with or without cache
    a.manage_permission(checked_permission, roles=[], acquire=1)
    b.manage_permission(checked_permission, roles=['Assignor'], acquire=0)
    login = PortalTestCase.login
    login(self, 'alice')
    self.assertEqual(
      [['', ''], ['A', '1'], ['B', '2'], ['B1', '2/21']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,))

    login(self, 'bob')
    self.assertEqual(
      [['', ''], ['A', '1']],
      bc.getCategoryChildTitleItemList(checked_permission=checked_permission,))

  def test_28_getCategoryChildItemListWithCheckedPermissionAndNoCache(self):
    self._testGetCategoryChildItemListWithCheckedPermission(cache=None)

  def test_28_getCategoryChildItemListWithCheckedPermissionAndCache(self):
    self._testGetCategoryChildItemListWithCheckedPermission(cache='erp5_ui_long')

  def test_29_renameBaseCategory(self):
    bc = self.portal.portal_categories.newContent(
                          portal_type='Base Category',
                          id='first_id')
    self.tic()
    bc.setId('new_id')
    self.assertEqual('new_id', bc.getId())

  def test_30_resolveCategory(self):
    portal = self.getPortal()
    category_tool = portal.portal_categories
    module = portal.sale_order_module
    order = module.newContent(id='foo', portal_type='Sale Order')
    self.assertNotEquals(order, None)
    line = order.newContent(id='bar', portal_type='Sale Order Line')
    self.assertNotEquals(line, None)
    cell = line.newContent(id='baz', portal_type='Sale Order Cell')
    self.assertNotEquals(cell, None)
    self.tic()

    for relative_url, value in (
            ('sale_order_module', module),
            ('sale_order_module/foo', order),
            ('sale_order_module/bar', None),
            ('sale_order_module/order', None),
            ('sale_order_module/sale_order_module', None),
            ('sale_order_module/foo/bar', line),
            ('sale_order_module/foo/foo', None),
            ('sale_order_module/foo/order', None),
            ('sale_order_module/foo/sale_order_module', None),
            ('sale_order_module/foo/bar/baz', cell),
            ('sale_order_module/foo/bar/bar', None),
            ('sale_order_module/foo/bar/foo', None),
            ('sale_order_module/foo/bar/order', None),
            ('sale_order_module/foo/bar/sale_order_module', None),
            ):
      obj = category_tool.resolveCategory(relative_url)
      self.assertEqual(obj, value)
      obj = category_tool.resolveCategory('order/' + relative_url)
      self.assertEqual(obj, value)
      obj = category_tool.resolveCategory('mapping/order/' + relative_url)
      self.assertEqual(obj, value)

  def test_31_assert_raise_if_base_category_is_missing(self):
    #First remove Base Category
    self.portal.portal_categories.manage_delObjects(['region'])
    obj = self.portal.person_module.newContent(portal_type='Person')
    self.commit()
    try:
      #Setters
      self.assertRaises(AttributeError, getattr, obj, 'setRegion')
      self.assertRaises(AttributeError, getattr, obj, 'setRegionValueList')
      self.assertRaises(AttributeError, getattr, obj, 'setRegionList')
      #getters
      self.assertRaises(AttributeError, getattr, obj, 'getRegion')
      self.assertRaises(AttributeError, getattr, obj, 'getRegionValueList')
      self.assertRaises(AttributeError, getattr, obj, 'getRegionList')
      # Tester are always present, because they are genereted on the BaseClass
      # during startup
      # self.assertRaises(AttributeError, getattr, obj, 'hasRegion')
    finally:
      #add Base Category
      self.portal.portal_categories.newContent(id='region', portal_type='Base Category')
    self.commit()
    #check Method exists after base_category creation
    #Setters
    self.assertTrue(getattr(obj, 'setRegion') is not None)
    self.assertTrue(getattr(obj, 'setRegionValueList') is not None)
    self.assertTrue(getattr(obj, 'setRegionList') is not None)
    #getters
    self.assertTrue(getattr(obj, 'getRegion') is not None)
    self.assertTrue(getattr(obj, 'getRegionValueList') is not None)
    self.assertTrue(getattr(obj, 'getRegionList') is not None)

  def test_CategoryTool_FolderInterface(self):
    # minimal tests for Folder methods on Category Tool
    category_tool = self.portal.portal_categories
    self.assertNotEquals([], list(category_tool.contentValues()))
    self.assertNotEquals([], list(category_tool.contentIds()))
    self.assertNotEquals([], list(category_tool.objectValues()))
    self.assertNotEquals([], list(category_tool.objectIds()))
    self.assertNotEquals([], list(category_tool.searchFolder()))

  def test_duplicate_base_category_id_in_categories_list_properties(self):
    """check that stored values like 'region/region/west' on categories property
    are cleaned up by Getters to avoid accessing base_category through
    implicit Acquisition.

    Even if region is a sub Category of Base Category region,
    Relative Url must be stripped.
    """
    portal_categories = self.getCategoriesTool()
    organisation = self.getOrganisationModule().newContent(
                                                  portal_type='Organisation',
                                                  region='region/europe/west')
    person = self.getPersonModule().newContent(portal_type='Person',
                              default_career_subordination_value=organisation)
    self.assertTrue(organisation.hasRegion())
    self.assertEqual(organisation.getRegion(), 'europe/west')
    self.assertEqual(organisation.getRegionList(), ['europe/west'])
    old_west_region = organisation.getRegionValue()
    self.assertEqual(old_west_region.getPortalType(), 'Category')

    # Check acquired categories
    self.assertEqual(person.getRegion(), 'europe/west')
    self.assertEqual(person.getRegionList(), ['europe/west'])

    region_base_category = portal_categories.region
    new_region = region_base_category.newContent(portal_type='Category',
                                                 id='region')
    new_region = new_region.newContent(portal_type='Category', id='europe')
    new_region = new_region.newContent(portal_type='Category', id='west')

    self.assertEqual(organisation.getRegion(), 'europe/west')
    self.assertEqual(organisation.getRegionList(), ['europe/west'])
    self.assertEqual(organisation.getRegionValue().getPortalType(), 'Category')
    self.assertEqual(organisation.getRegionValue(), old_west_region)

    self.assertEqual(person.getRegion(), 'europe/west')
    self.assertEqual(person.getRegionList(), ['europe/west'])

    # Let's continue with resource because its ID conflict with
    # "traversing namespaces" names
    resource_value = portal_categories.resource.newContent(portal_type='Category', id='id1')
    organisation.setResource('resource/id1')
    self.assertEqual(organisation.getResource(), 'id1')
    self.assertEqual(organisation.getResourceValue(), resource_value)
    self.assertEqual(organisation.getResourceList(), ['id1'])
    self.assertEqual(organisation.getResourceValue(portal_type='Category'),
                      resource_value)
    self.assertEqual(organisation.getResourceValueList(portal_type='Category'),
                      [resource_value])

    # Check other public methods of CategoryTool
    self.assertEqual(portal_categories.getCategoryMembershipList(organisation,
                                           'resource', portal_type='Category'),
                      ['id1'])
    self.assertEqual(portal_categories.getSingleCategoryMembershipList(
                                                    organisation, 'resource',
                                                    portal_type='Category'),
                      ['id1'])
    # Check indexation
    self.tic()

  def test_setCategoryMemberShip(self):
    person = self.getPersonModule().newContent(portal_type='Person')
    category_tool = self.getCategoriesTool()
    bc = category_tool.newContent()
    bc.newContent('a')
    bc.newContent('b')
    base = (bc.id + '/').__add__
    def get(*args, **kw):
      return category_tool.getCategoryMembershipList(person, *args, **kw)
    def _set(*args, **kw):
      return category_tool._setCategoryMembership(person, *args, **kw)
    _set(bc.id, list('aa'))
    self.assertEqual(get(bc.id), list('aa'))
    _set(bc.id, list('baa'))
    self.assertEqual(get(bc.id), list('aba'))
    _set(bc.id, map(base, 'bb'), 1)
    self.assertEqual(get(bc.id), list('bb'))
    _set(bc.id, map(base, 'abb'), 1)
    self.assertEqual(get(bc.id), list('bab'))
    _set(bc.id, ())

  def test_relatedIndex(self):
    category_tool = self.getCategoriesTool()
    newOrganisation = self.getOrganisationModule().newContent
    organisation = newOrganisation()
    other_organisation = newOrganisation(destination_value=organisation)
    person = self.getPersonModule().newContent(test0_value=organisation,
                                               test1='a/ac/acd')
    self.tic()
    get = organisation.getTest0RelatedValueList
    a = category_tool.test1.a
    def check():
      self.assertEqual([person, other_organisation],
        category_tool.getRelatedValueList(organisation))
      self.assertEqual([person], get())
      self.assertEqual([person], get(portal_type='Person'))
      self.assertEqual([], get(portal_type='Organisation'))
      self.assertEqual([person], a.getTest1RelatedValueList(
        portal_type='Person'))
      self.assertEqual([a], a.getTest1RelatedValueList(
        strict_membership=True))
      self.assertEqual([person], a.ac.acd.getTest1RelatedValueList(
        portal_type='Person', strict_membership=True))
    category_tool.test0._setRelatedLocallyIndexed(True)
    category_tool.test1._setRelatedLocallyIndexed(True)
    check()
    related_list = sorted(a.getTest1RelatedList())
    self.assertTrue(person.getRelativeUrl() in related_list)
    self.assertEqual(related_list, sorted(x.getRelativeUrl()
      for x in self.portal.portal_catalog(test1_uid=a.getUid())))
    related = organisation._related_index
    self.assertTrue(related)
    self.assertEqual([person.getRelativeUrl()], list(related.test0))
    person.unindexObject()
    self.tic()
    category_tool.test0._setRelatedLocallyIndexed(False)
    self.assertEqual([], get())
    category_tool.test0._setRelatedLocallyIndexed(True)
    check()
    person.categories = tuple(x for x in person.categories
                                if not x.startswith('test0/'))
    self.assertEqual([], get())
    self.assertFalse(related)
    self.assertEqual([], list(related.test0))
    related = a.ac.acd._related_index.test1
    self.assertEqual(list(related), [person.getRelativeUrl()])
    person._setTest1Value(a)
    self.assertEqual(list(related), [])
    
  def test_Category_setCategoryValue(self):
    # Test all case of setting categories values
    region_value = self.portal.portal_categories.resolveCategory('region/europe')
    region_value2 = self.portal.portal_categories.resolveCategory('region/europe/west')
    self.assertNotEqual(None,region_value)
    self.assertNotEqual(None,region_value2)
    
    newPerson = self.getPersonModule().newContent
    person = newPerson()
    person.setRegionValue(region_value)
    person2 = newPerson(region_value=region_value2)
    
    self.tic()
    
    self.assertEqual(person.getRegion(), 'europe')
    self.assertTrue('region/europe' in person.getCategoryList())
    self.assertEqual(person2.getRegion(), 'europe/west')
    self.assertTrue('region/europe/west' in person2.getCategoryList())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestCMFCategory))
  return suite

