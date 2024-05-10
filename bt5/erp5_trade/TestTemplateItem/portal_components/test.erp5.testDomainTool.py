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


from erp5.component.test.testPredicate import TestPredicateMixIn, \
    REGION_FRANCE_PATH, REGION_GERMANY_PATH, GROUP_STOREVER_PATH
from DateTime import DateTime
from Products.ZSQLCatalog.SQLCatalog import Query

class TestDomainTool(TestPredicateMixIn):

  # Different variables used for this test
  run_all_test = 1
  resource_type='Apparel Component'
  resource_variation_type='Apparel Component Variation'
  resource_module = 'apparel_component_module'

  def getTitle(self):
    """
    """
    return "Domain Tool"

  def getBusinessTemplateList(self):
    """
      Return the list of business templates.

    """
    return ('erp5_base','erp5_pdm', 'erp5_simulation', 'erp5_trade', 'erp5_apparel')

  def afterSetUp(self):
    domain_tool = self.getDomainTool()

    # Query to restrict searches to 'interesting' predicates:
    # - ignore simulation rules, which are now predicates
    # - ignore as well constraints, which are predicates
    self.portal_type_query = Query(
        operator='AND',
        portal_type=['!=%s' % x for x
          in domain_tool.getPortalRuleTypeList()
          + ('Base Domain', 'Contribution Predicate',
             'Solver Type', 'Trade Model Path', 'Worklist')
          + domain_tool.getPortalDivergenceTesterTypeList()
          + domain_tool.getPortalBusinessProcessTypeList()
          + domain_tool.getPortalBusinessLinkTypeList()
          + domain_tool.getPortalConstraintTypeList()])
    super(TestDomainTool, self).afterSetUp()

  def beforeTearDown(self):
    self.abort()

    for system_preference in self.portal.portal_preferences.objectValues(portal_type='System Preference'):
      if system_preference.getPreferenceState() != 'disabled':
        system_preference.disable()
    def deleteAll(module):
      module.manage_delObjects(ids=list(module.objectIds()))
    deleteAll(self.portal.organisation_module)
    deleteAll(self.portal.product_module)
    deleteAll(self.portal.sale_supply_module)
    deleteAll(self.portal.sale_order_module)

    self.tic()

  def getPortalId(self):
    return self.getPortal().getId()

  def getResourceModule(self):
    return getattr(self.getPortal(), self.resource_module, None)

  def getSaleOrderModule(self):
    return getattr(self.getPortal(),'sale_order_module',None)

  def getOrderLine(self):
    return self.getSaleOrderModule()['1']['1']

  def getPredicate(self):
    return self.getOrganisationModule()['1']

  def createData(self):
    # We have no place to put a Predicate, we will put it in a
    # Organisation Module
    organisation_module = self.getOrganisationModule()
    module_type = organisation_module.getTypeInfo()
    content_type_set = set(module_type.getTypeAllowedContentTypeList())
    content_type_set.add('Mapped Value')
    module_type._setTypeAllowedContentTypeList(tuple(content_type_set))
    if organisation_module.hasContent('1'):
      organisation_module.deleteContent('1')
    predicate = organisation_module.newContent(id='1',portal_type='Mapped Value')
    predicate.setCriterion('quantity',identity=None,min=None,max=None)

    resource_module = self.getResourceModule()
    if resource_module.hasContent('1'):
      resource_module.deleteContent('1')
    self.resource = resource = resource_module.newContent(id='1',portal_type=self.resource_type)
    resource.newContent(id='blue',portal_type=self.resource_variation_type)
    resource.newContent(id='red',portal_type=self.resource_variation_type)
    resource.setVariationBaseCategoryList(['variation'])
    if resource.hasContent('default_supply_line'):
      resource.deleteContent('default_supply_line')
    self.supply_line = resource.newContent(id='default_supply_line',portal_type='Supply Line')

    # Then create an order with a particular line
    order_module = self.getSaleOrderModule()
    if order_module.hasContent('1'):
      order_module.deleteContent('1')
    order = order_module.newContent(id='1',portal_type='Sale Order')
    order.newContent(id='1',portal_type='Sale Order Line')

    # Then create a base category
    portal_categories = self.getCategoryTool()
    for bc in ('region', ):
      if not hasattr(portal_categories, bc):
        portal_categories.newContent(portal_type='Base Category',id=bc)
      portal_categories[bc].setAcquisitionMaskValue(1)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      if not 'europe' in portal_categories[bc].objectIds():
        portal_categories[bc].newContent(id='europe',portal_type='Category')
      if not 'africa' in portal_categories[bc].objectIds():
        portal_categories[bc].newContent(id='africa',portal_type='Category')
      if not 'asia' in portal_categories[bc].objectIds():
        portal_categories[bc].newContent(id='asia',portal_type='Category')

    self.tic()

  def checkPredicate(self, test=None):
    predicate = self.getPredicate()
    order_line = self.getOrderLine()
    searchPredicateList = self.getDomainTool().searchPredicateList
    def assertPredicateItemsMatchingOrderLineEqual(expected, **kw):
      self.tic()
      self.assertCountEqual(
        expected,
        searchPredicateList(order_line, test=test, **kw),
      )

    # Test with order line and predicate to none
    # Actually, a predicate where nothing is defined is ok
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type=self.portal_type_query)
    # Test with order line not none and predicate to none
    order_line.setQuantity(45)
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type=self.portal_type_query)
    # Test with order line not none and predicate to identity
    order_line.setQuantity(45)
    predicate.setCriterion('quantity', identity=45, min=None, max=None)
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type='Mapped Value')
    order_line.setQuantity(40)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    # Test with order line not none and predicate to min
    order_line.setQuantity(45)
    predicate.setCriterion('quantity', identity=None, min=30, max=None)
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type='Mapped Value')
    order_line.setQuantity(10)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type=self.portal_type_query) # XXX: mistake in the test ?
    # Test with order line not none and predicate to max
    order_line.setQuantity(45)
    predicate.setCriterion('quantity', identity=None, min=None, max=50)
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type='Mapped Value')
    order_line.setQuantity(60)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    # Test with order line not none and predicate to min max
    order_line.setQuantity(20)
    predicate.setCriterion('quantity', identity=None, min=30, max=50)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    order_line.setQuantity(60)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    order_line.setQuantity(45)
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type='Mapped Value')
    # Test with order line not none and predicate to min max
    # and also predicate to a category
    predicate.setMembershipCriterionBaseCategoryList(['region'])
    predicate.setMembershipCriterionCategoryList(['region/europe'])
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    order_line.setCategoryList(['region/africa'])
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    order_line.setCategoryList(['region/europe'])
    assertPredicateItemsMatchingOrderLineEqual([predicate], portal_type='Mapped Value')
    order_line.setQuantity(60)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Mapped Value')
    # Test with order line not none and predicate to date min and date max
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    order_line.setDefaultResourceValue(self.resource)
    self.assertEqual(self.supply_line.getDefaultResourceValue(), self.resource)
    self.assertEqual(order_line.getDefaultResourceValue(), self.resource)
    date1 = DateTime('2005/04/08 10:47:26.388 GMT-4')
    date2 = DateTime('2005/04/10 10:47:26.388 GMT-4')
    self.supply_line.setStartDateRangeMin(date1)
    self.supply_line.setStartDateRangeMax(date2)
    current_date = DateTime('2005/04/1 10:47:26.388 GMT-4')
    order_line.setStartDate(current_date)
    assertPredicateItemsMatchingOrderLineEqual([], portal_type='Supply Line')
    current_date = DateTime('2005/04/09 10:47:26.388 GMT-4')
    order_line.setStartDate(current_date)
    assertPredicateItemsMatchingOrderLineEqual([self.supply_line], portal_type='Supply Line')

  def test_01_SearchPredidateListWithNoTest(self):
    self.createData()
    self.checkPredicate(test=0)

  def test_02_SearchPredidateListWithTest(self):
    self.createData()
    self.checkPredicate(test=1)

  def test_03_GenerateMappedValue(self):
    self.createData()
    self.supply_line.setVariationBaseCategoryList(['colour'])
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    #self.supply_line.setMultimembershipCriterionBaseCategoryList(['resource'])
    self.supply_line.setMappedValuePropertyList(['base_price','priced_quantity'])
    #self.supply_line.setMembershipCriterionCategoryList(['resource/%s' % self.resource.getRelativeUrl()])
    self.tic()
    domain_tool = self.getDomainTool()
    context = self.resource.asContext(categories=['resource/%s' % self.resource.getRelativeUrl()])
    mapped_value = domain_tool.generateMappedValue(context, portal_type="Supply Line")
    self.assertEqual(mapped_value.getBasePrice(),23)

  def test_04_GenerateMappedValueWithRanges(self):
    self.createData()
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    date1 = DateTime('2005/04/08')
    date2 = DateTime('2005/04/10')
    self.supply_line.setStartDateRangeMin(date1)
    self.supply_line.setStartDateRangeMax(date2)
    self.supply_line.setMappedValuePropertyList(['base_price','priced_quantity'])
    self.tic()
    domain_tool = self.getDomainTool()
    order_line = self.getOrderLine()
    order_line.setDefaultResourceValue(self.resource)
    current_date = DateTime('2005/04/01')
    order_line.setStartDate(current_date)
    kw = {'portal_type':('Supply Line','Supply Cell')}
    mapped_value = domain_tool.generateMappedValue(order_line,**kw)
    self.assertEqual(mapped_value,None)
    current_date = DateTime('2005/04/09')
    order_line.setStartDate(current_date)
    mapped_value = domain_tool.generateMappedValue(order_line,**kw)
    self.assertEqual(mapped_value.getBasePrice(),23)

  def test_05_GenerateMappedValueWithVariation(self):
    self.createData()
    self.supply_line.setVariationBaseCategoryList(['colour'])
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    self.supply_line.setMappedValuePropertyList(['base_price','priced_quantity'])
    self.resource.setPVariationBaseCategoryList(['variation'])
    self.supply_line.updateCellRange(base_id='path')
    cell_range = self.supply_line.SupplyLine_asCellRange()
    for range_ in cell_range[0]:
      cell = self.supply_line.newCell(range_,base_id='path',portal_type='Supply Cell')
      cell.setMappedValuePropertyList(['base_price','priced_quantity'])
      cell.setMultimembershipCriterionBaseCategoryList(['resource','variation'])
      cell.setPricedQuantity(1)
      if range_.find('blue')>=0:
        cell.setMembershipCriterionCategoryList([range_])
        cell.setBasePrice(45)
      if range_.find('red')>=0:
        cell.setMembershipCriterionCategoryList([range_])
        cell.setBasePrice(26)

    right_price_list = [45,26]
    price_list = [x.getBasePrice() for x in self.supply_line.objectValues()]
    self.failIfDifferentSet(price_list,right_price_list)

    def sort_method(x,y):
      # make sure we get cell before
      if hasattr(x,'hasCellContent'):
        x_cell = x.hasCellContent(base_id='path')
        if x_cell:
          return 1
      if hasattr(y,'hasCellContent'):
        y_cell = y.hasCellContent(base_id='path')
        if y_cell:
          return -1
      return 0

    def sort_key_method(x):
      hasCellContent = getattr(x, 'hasCellContent', None)
      return bool(hasCellContent and hasCellContent(base_id='path'))

    self.tic()
    domain_tool = self.getDomainTool()
    context = self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/blue' % self.resource.getRelativeUrl()])
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_method=sort_method)
    self.assertEqual(mapped_value.getProperty('base_price'),45)
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_key_method=sort_key_method)
    self.assertEqual(mapped_value.getProperty('base_price'),45)
    context = self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/red' % self.resource.getRelativeUrl()])
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_method=sort_method)
    self.assertEqual(mapped_value.getProperty('base_price'),26)
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_key_method=sort_key_method)
    self.assertEqual(mapped_value.getProperty('base_price'),26)
    # Now check the price
    self.assertEqual(self.resource.getPrice(context=self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/blue' % self.resource.getRelativeUrl()]),
                     sort_method=sort_method),45)
    self.assertEqual(self.resource.getPrice(context=self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/blue' % self.resource.getRelativeUrl()]),
                     sort_key_method=sort_key_method),45)

  def test_06_SQLQueryDoesNotReturnTooManyPredicates(self):
    predicate_both_match = self.createPredicate(
        multimembership_criterion_base_category_list=['group', 'region'],
        membership_criterion_category_list=[GROUP_STOREVER_PATH, REGION_FRANCE_PATH])
    predicate_one_match = self.createPredicate(
        multimembership_criterion_base_category_list=['group', 'region'],
        membership_criterion_category_list=[GROUP_STOREVER_PATH, REGION_GERMANY_PATH])
    document = self.createDocument(group='nexedi/storever',
                                   region='europe/western_europe/france')
    self.tic()
    portal_domains = self.getPortalObject().portal_domains
    # Basic sanity checks
    self.assertTrue(predicate_both_match.test(document))
    self.assertFalse(predicate_one_match.test(document))
    self.assertNotIn(predicate_one_match, portal_domains.searchPredicateList(document, portal_type=self.portal_type_query, test=1))
    # Real test
    self.assertNotIn(predicate_one_match, portal_domains.searchPredicateList(document, portal_type=self.portal_type_query, test=0))

  def test_07_NonLeftJoinModeOfSearchPredicateList(self):
    searchPredicateList = self.portal.portal_domains.searchPredicateList
    # Add system preference
    system_preference = self.portal.portal_preferences.newContent(portal_type='System Preference')
    system_preference.setPreferredPredicateCategoryList(['source_section', 'destination_section', 'price_currency'])
    # Add sample data
    jpy = self.portal.currency_module.newContent(portal_type='Currency', title='JPY', reference='JPY')
    jpy.validate()
    euro = self.portal.currency_module.newContent(portal_type='Currency', title='EURO', reference='EUR')
    euro.validate()
    newOrganisation = self.portal.organisation_module.newContent
    company= newOrganisation(portal_type='Organisation', title='Company')
    shop = newOrganisation(portal_type='Organisation', title='Shop')
    supplier = newOrganisation(portal_type='Organisation', title='Supplier')
    product_module = self.portal.product_module
    product1 = product_module.newContent(portal_type='Product', title='Product1')
    product2 = product_module.newContent(portal_type='Product', title='Product2')
    supply_module = self.portal.sale_supply_module
    supply1 = supply_module.newContent(portal_type='Sale Supply', title='Supply1', source_section_value=supplier, destination_section_value=shop, price_currency_value=jpy)
    supply1.validate()
    supply1_line1 = supply1.newContent(portal_type='Sale Supply Line', resource_value=product1)
    supply1_line2 = supply1.newContent(portal_type='Sale Supply Line', resource_value=product2)
    supply2 = supply_module.newContent(portal_type='Sale Supply', title='Supply2', source_section_value=supplier, destination_section_value=company, price_currency_value=jpy)
    supply2.validate()
    supply2_line1 = supply2.newContent(portal_type='Sale Supply Line', resource_value=product2)
    supply3 = supply_module.newContent(portal_type='Sale Supply', title='Supply3', source_section_value=supplier, price_currency_value=euro)
    supply3.validate()
    supply3_line1 = supply3.newContent(portal_type='Sale Supply Line', resource_value=product1)
    order = self.portal.sale_order_module.newContent(
      portal_type='Sale Order',
      source_section_value=supplier,
      destination_section_value=shop,
      price_currency_value=jpy)
    order_line = order.newContent(
      portal_type='Sale Order Line',
      resource_value=product1,
    )
    self.tic()

    def assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(uses_left_join, expected, **kw):
      kw['context'] = order_line
      kw['portal_type'] = 'Sale Supply Line'
      src = searchPredicateList(src__=1, **kw)
      if uses_left_join:
        self.assertIn('LEFT JOIN', src)
      else:
        self.assertNotIn('LEFT JOIN', src)
      self.assertCountEqual(expected, searchPredicateList(**kw))

    # Check left join mode
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1, supply1_line2, supply2_line1, supply3_line1], tested_base_category_list=['source_section'])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1, supply1_line2, supply3_line1], tested_base_category_list=['source_section', 'destination_section'])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1, supply1_line2], tested_base_category_list=['source_section', 'destination_section', 'price_currency'])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1], tested_base_category_list=['source_section', 'destination_section', 'price_currency', 'resource'])

    # Check inner-join mode
    # Enable system preference and reindex relevant predicates
    system_preference.enable()
    self.tic()
    supply_module.recursiveReindexObject()
    self.tic()
    # if document has relations using base categories which are not present in the preference, then left join mode is still used.
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(False, [supply1_line1, supply1_line2, supply2_line1, supply3_line1], tested_base_category_list=['source_section'])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(False, [supply1_line1, supply1_line2, supply3_line1], tested_base_category_list=['source_section', 'destination_section'])
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(False, [supply1_line1, supply1_line2], tested_base_category_list=['source_section', 'destination_section', 'price_currency'])
    # resource is not in preferred predicate category list, so left join is used
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(True, [supply1_line1], tested_base_category_list=['source_section', 'destination_section', 'price_currency', 'resource'])
    # add resource to preference, this enables non-left join mode
    system_preference.setPreferredPredicateCategoryList(['source_section', 'destination_section', 'price_currency', 'resource'])
    self.portal.portal_caches.clearAllCache()
    self.tic()
    supply_module.recursiveReindexObject()
    self.tic()
    # resource is not in preferred predicate category list, so only inner join is used
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(False, [supply1_line1], tested_base_category_list=['source_section', 'destination_section', 'price_currency', 'resource'])
    # we now cover all categories defined on order_line, so it uses inner-join only even if tested_base_category_list is not specified.
    assertUsesLeftJoinAndPredicateItemsMatchingOrderLineEqual(False, [supply1_line1])

    # unknown base category ids cause an exception, so typos are detected
    self.assertRaises(
      ValueError,
      searchPredicateList,
      context=order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['BOOO'],
    )
    # known Base Categories but for which context has no relation also raise.
    self.assertRaises(
      ValueError,
      searchPredicateList,
      context=order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['colour'],
    )

  def test_searchPredicateInvalidCategories(self):
    predicate = self.portal.sale_supply_module.newContent(
      portal_type='Sale Supply')
    predicate.validate()
    self.assertNotEqual(predicate.asPredicate(), None)

    context = self.portal.person_module.newContent(
      portal_type='Person',
      region=('broken/category'))

    # An invalid category should raise explicitly, for all parameters of
    # searchPredicateList ( the code paths are different )
    self.assertRaises(TypeError, self.portal.portal_domains.searchPredicateList,
      context=context, portal_type=predicate.portal_type)
    self.assertRaises(TypeError, self.portal.portal_domains.searchPredicateList,
      context=context, portal_type=predicate.portal_type, acquired=False)
    self.assertRaises(TypeError, self.portal.portal_domains.searchPredicateList,
      context=context, portal_type=predicate.portal_type,
      tested_base_category_list=['region'])
    self.assertRaises(TypeError, self.portal.portal_domains.searchPredicateList,
      context=context, portal_type=predicate.portal_type,
      tested_base_category_list=['region'], acquired=False)

    # This is also the case if there are multiple categories (another code
    # path)
    context = self.portal.person_module.newContent(
      portal_type='Person',
      region=('broken/category', 'region'))
    self.assertRaises(TypeError, self.portal.portal_domains.searchPredicateList,
      context=context, portal_type=predicate.portal_type)


  def test_setRelationToBaseDomain(self):
    # category accessors can be useed to set relations to base domains.
    base_domain = self.portal.portal_domains.newContent(
      portal_type='Base Domain')
    # get a document with source accessor
    document = self.portal.sale_order_module.newContent(
      portal_type='Sale Order')

    document.setSourceValue(base_domain)
    self.assertEqual(base_domain, document.getSourceValue())

  def test_setRelationToDomain(self):
    # category accessors can be useed to set relations to domains.
    base_domain = self.portal.portal_domains.newContent(
      portal_type='Base Domain')
    domain = base_domain.newContent(portal_type='Domain')
    # get a document with source accessor
    document = self.portal.sale_order_module.newContent(
      portal_type='Sale Order')

    document.setSourceValue(domain)
    self.assertEqual(domain, document.getSourceValue())


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDomainTool))
  return suite

