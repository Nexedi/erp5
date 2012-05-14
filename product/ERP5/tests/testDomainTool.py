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


from Products.ERP5.tests.testPredicate import TestPredicateMixIn, \
    REGION_FRANCE_PATH, REGION_GERMANY_PATH, GROUP_STOREVER_PATH
from DateTime import DateTime
from zLOG import LOG
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
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_apparel')

  def afterSetUp(self):
    domain_tool = self.getDomainTool()

    # Query to restrict searches to 'interesting' predicates:
    # - ignore simulation rules, which are now predicates
    # - ignore as well constraints, which are predicates
    self.portal_type_query = Query(
        operator='AND',
        portal_type=['!=%s' % x for x
          in domain_tool.getPortalRuleTypeList()
          + ('Base Domain', 'Contribution Predicate')
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
    self.supply_line = supply_line = resource.newContent(id='default_supply_line',portal_type='Supply Line')

    # Then create an order with a particular line
    order_module = self.getSaleOrderModule()
    if order_module.hasContent('1'):
      order_module.deleteContent('1')
    order = order_module.newContent(id='1',portal_type='Sale Order')
    line = order.newContent(id='1',portal_type='Sale Order Line')

    # Then create a base category
    portal_categories = self.getCategoryTool()
    for bc in ('region', ):
      if not hasattr(portal_categories, bc):
        portal_categories.newContent(portal_type='Base Category',id=bc)
      portal_categories[bc].setAcquisitionMaskValue(1)
      portal_categories[bc].setAcquisitionCopyValue(0)
      portal_categories[bc].setAcquisitionAppendValue(0)
      if not 'europe' in portal_categories[bc].objectIds():
        big_region = portal_categories[bc].newContent(id='europe',portal_type='Category')
      if not 'africa' in portal_categories[bc].objectIds():
        big_region = portal_categories[bc].newContent(id='africa',portal_type='Category')
      if not 'asia' in portal_categories[bc].objectIds():
        big_region = portal_categories[bc].newContent(id='asia',portal_type='Category')

    self.tic()

  def checkPredicate(self, test=None):

    predicate = self.getPredicate()
    #predicate.setMembershipCriterionBaseCategoryList([])
    #predicate.setMembershipCriterionCategoryList([])
    #predicate.setCriterion('quantity',identity=45,min=None,max=None)
    #predicate.immediateReindexObject()


    order_line = self.getOrderLine()
    domain_tool = self.getDomainTool()

    # Test with order line and predicate to none
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,
        portal_type=self.portal_type_query)
    self.assertEquals(len(predicate_list),1) # Actually, a predicate where
                                             # nothing is defined is ok

    # Test with order line not none and predicate to none
    order_line.setQuantity(45)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,
        portal_type=self.portal_type_query)
    self.assertEquals(len(predicate_list),1)

    # Test with order line not none and predicate to identity
    order_line.setQuantity(45)
    kw = {'portal_type':'Mapped Value'}
    predicate.setCriterion('quantity',identity=45,min=None,max=None)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),1)

    order_line.setQuantity(40)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to min
    order_line.setQuantity(45)
    predicate = self.getPredicate()
    predicate.setCriterion('quantity',identity=None,min=30,max=None)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),1)

    order_line.setQuantity(10)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,
        portal_type=self.portal_type_query)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to max
    order_line.setQuantity(45)
    predicate = self.getPredicate()
    predicate.setCriterion('quantity',identity=None,min=None,max=50)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),1)

    order_line.setQuantity(60)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to min max
    order_line.setQuantity(20)
    predicate = self.getPredicate()
    predicate.setCriterion('quantity',identity=None,min=30,max=50)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    order_line.setQuantity(60)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    order_line.setQuantity(45)
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.tic()
    self.assertEquals(len(predicate_list),1)

    # Test with order line not none and predicate to min max
    # and also predicate to a category
    predicate.setMembershipCriterionBaseCategoryList(['region'])
    predicate.setMembershipCriterionCategoryList(['region/europe'])
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    order_line.setCategoryList(['region/africa'])
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    order_line.setCategoryList(['region/europe'])
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),1)

    order_line.setQuantity(60)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    # Test with order line not none and predicate to date min and date max
    kw = {'portal_type':'Supply Line'}
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    order_line.setDefaultResourceValue(self.resource)
    self.assertEquals(self.supply_line.getDefaultResourceValue(),self.resource)
    self.assertEquals(order_line.getDefaultResourceValue(),self.resource)
    date1 = DateTime('2005/04/08 10:47:26.388 GMT-4')
    date2 = DateTime('2005/04/10 10:47:26.388 GMT-4')
    self.supply_line.setStartDateRangeMin(date1)
    self.supply_line.setStartDateRangeMax(date2)
    current_date = DateTime('2005/04/1 10:47:26.388 GMT-4')
    order_line.setStartDate(current_date)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),0)

    current_date = DateTime('2005/04/09 10:47:26.388 GMT-4')
    order_line.setStartDate(current_date)
    self.tic()
    predicate_list = domain_tool.searchPredicateList(order_line,test=test,**kw)
    self.assertEquals(len(predicate_list),1)

  def test_01_SearchPredidateListWithNoTest(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Search Predicate List With No Test')
    self.createData()
    self.checkPredicate(test=0)

  def test_02_SearchPredidateListWithTest(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Search Predicate List With Test')
    self.createData()
    self.checkPredicate(test=1)

  def test_03_GenerateMappedValue(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Generate Mapped Value')
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
    self.assertEquals(mapped_value.getBasePrice(),23)

  def test_04_GenerateMappedValueWithRanges(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Generate Mapped Value With Ranges')
    self.createData()
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    date1 = DateTime('2005/04/08')
    date2 = DateTime('2005/04/10')
    self.supply_line.setStartDateRangeMin(date1)
    self.supply_line.setStartDateRangeMax(date2)
    LOG('Test04, supply_line.getStartDateRangeMin',0,self.supply_line.getStartDateRangeMin())
    LOG('Test04, supply_line.getStartDateRangeMax',0,self.supply_line.getStartDateRangeMax())
    self.supply_line.setMappedValuePropertyList(['base_price','priced_quantity'])
    self.tic()
    domain_tool = self.getDomainTool()
    order_line = self.getOrderLine()
    order_line.setDefaultResourceValue(self.resource)
    current_date = DateTime('2005/04/01')
    order_line.setStartDate(current_date)
    kw = {'portal_type':('Supply Line','Supply Cell')}
    mapped_value = domain_tool.generateMappedValue(order_line,**kw)
    self.assertEquals(mapped_value,None)
    current_date = DateTime('2005/04/09')
    order_line.setStartDate(current_date)
    mapped_value = domain_tool.generateMappedValue(order_line,**kw)
    self.assertEquals(mapped_value.getBasePrice(),23)

  def test_05_GenerateMappedValueWithVariation(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Generate Mapped Value With Variation')
    self.createData()
    self.supply_line.setVariationBaseCategoryList(['colour'])
    self.supply_line.setBasePrice(23)
    self.supply_line.setPricedQuantity(1)
    self.supply_line.setDefaultResourceValue(self.resource)
    self.supply_line.setMappedValuePropertyList(['base_price','priced_quantity'])
    self.resource.setPVariationBaseCategoryList(['variation'])
    self.supply_line.updateCellRange(base_id='path')
    cell_range = self.supply_line.SupplyLine_asCellRange()
    for range in cell_range[0]:
      cell = self.supply_line.newCell(range,base_id='path',portal_type='Supply Cell')
      cell.setMappedValuePropertyList(['base_price','priced_quantity'])
      cell.setMultimembershipCriterionBaseCategoryList(['resource','variation'])
      LOG('test, range',0,range)
      cell.setPricedQuantity(1)
      if range.find('blue')>=0:
        cell.setMembershipCriterionCategoryList([range])
        cell.setBasePrice(45)
      if range.find('red')>=0:
        cell.setMembershipCriterionCategoryList([range])
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
    self.assertEquals(mapped_value.getProperty('base_price'),45)
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_key_method=sort_key_method)
    self.assertEquals(mapped_value.getProperty('base_price'),45)
    context = self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/red' % self.resource.getRelativeUrl()])
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_method=sort_method)
    self.assertEquals(mapped_value.getProperty('base_price'),26)
    mapped_value = domain_tool.generateMappedValue(context,
                     portal_type=self.portal_type_query,
                     sort_key_method=sort_key_method)
    self.assertEquals(mapped_value.getProperty('base_price'),26)
    # Now check the price
    self.assertEquals(self.resource.getPrice(context=self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/blue' % self.resource.getRelativeUrl()]),
                     sort_method=sort_method),45)
    self.assertEquals(self.resource.getPrice(context=self.resource.asContext(
                     categories=['resource/%s' % self.resource.getRelativeUrl(),
                     'variation/%s/blue' % self.resource.getRelativeUrl()]),
                     sort_key_method=sort_key_method),45)

  def test_06_SQLQueryDoesNotReturnTooManyPredicates(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Check that SQL query does not return unneeded predicates')
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
    self.assertTrue(predicate_one_match not in portal_domains.searchPredicateList(document, portal_type=self.portal_type_query, test=1))
    # Real test
    self.assertTrue(predicate_one_match not in portal_domains.searchPredicateList(document, portal_type=self.portal_type_query, test=0))

  def test_07_NonLeftJoinModeOfSearchPredicateList(self, quiet=0, run=run_all_test):
    if not run: return
    if not quiet:
      self.logMessage('Test non-left join mode of searchPredicateList method')

    # Add system preference
    system_preference = self.portal.portal_preferences.newContent(portal_type='System Preference')
    system_preference.setPreferredPredicateCategoryList(
      ['source_section', 'destination_section', 'price_currency'])

    self.tic()

    # Add sample data
    jpy = self.portal.currency_module.newContent(portal_type='Currency',
                                                 title='JPY',
                                                 reference='JPY')
    jpy.validate()

    euro = self.portal.currency_module.newContent(portal_type='Currency',
                                                 title='EURO',
                                                 reference='EUR')
    euro.validate()

    organisation_module = self.portal.organisation_module
    company= organisation_module.newContent(portal_type='Organisation',
                                            title='Company')
    shop = organisation_module.newContent(portal_type='Organisation',
                                          title='Shop')
    supplier = organisation_module.newContent(portal_type='Organisation',
                                              title='Supplier')

    product_module = self.portal.product_module
    product1 = product_module.newContent(portal_type='Product',
                                         title='Product1')
    product2 = product_module.newContent(portal_type='Product',
                                         title='Product2')

    supply_module = self.portal.sale_supply_module
    supply1 = supply_module.newContent(portal_type='Sale Supply',
                                       title='Supply1',
                                       source_section_value=supplier,
                                       destination_section_value=shop,
                                       price_currency_value=jpy)
    supply1.newContent(portal_type='Sale Supply Line',
                       resource_value=product1)
    supply1.newContent(portal_type='Sale Supply Line',
                       resource_value=product2)
    supply2 = supply_module.newContent(portal_type='Sale Supply',
                                       title='Supply2',
                                       source_section_value=supplier,
                                       destination_section_value=company,
                                       price_currency_value=jpy)
    supply2.newContent(portal_type='Sale Supply Line',
                       resource_value=product2)
    supply3 = supply_module.newContent(portal_type='Sale Supply',
                                       title='Supply3',
                                       source_section_value=supplier,
                                       price_currency_value=euro)
    supply3.newContent(portal_type='Sale Supply Line',
                       resource_value=product1)

    order = self.portal.sale_order_module.newContent(
      portal_type='Sale Order',
      source_section_value=supplier,
      destination_section_value=shop,
      price_currency_value=jpy)
    order_line = order.newContent(portal_type='Sale Order Line',
                                  resource_value=product1)

    self.tic()

    # Test
    # Check traditional left join mode
    domain_tool = self.portal.portal_domains
    searchPredicateList = domain_tool.searchPredicateList
    self.assertEqual(len(
      searchPredicateList(order_line,
                          portal_type='Sale Supply Line')),
                     1)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section'])),
                     4)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency'],
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section'])),
                     3)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section'],
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency'])),
                     2)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency'],
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency', 'resource'])),
                     1)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency', 'resource'],
      src__=1))
    # if wrong base categories are passed, then nothing is matched
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['WAAA', 'BOOO'])),
                     0)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['WAAA', 'BOOO'],
      src__=1))

    # Check non-left join mode
    # Enable system preference and reindex all
    system_preference.enable()
    self.tic()
    self.portal.ERP5Site_reindexAll()
    self.tic()

    # if tested_base_category_list is not passed, then left join mode is
    # still used.
    self.assertEqual(len(
      searchPredicateList(order_line,
                          portal_type='Sale Supply Line')),
                     1)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      src__=1))

    
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section'])),
                     4)
    self.assert_(not 'LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency'],
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section'])),
                     3)
    self.assert_(not 'LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section'],
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency'])),
                     2)
    self.assert_(not 'LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency'],
      src__=1))
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency', 'resource'])),
                     1)
    # resource is not in preferred predicate category list, so left join
    # is used
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['source_section', 'destination_section',
                                 'price_currency', 'resource'],
      src__=1))
    # if wrong base categories are passed, then nothing is matched
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['WAAA', 'BOOO'])),
                     0)
    self.assert_('LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['WAAA', 'BOOO'],
      src__=1))
    # add WAAA and BOOO to preference, this enables non-left join mode
    system_preference.setPreferredPredicateCategoryList(
      ['source_section', 'destination_section', 'price_currency',
       'WAAA', 'BOOO'])
    self.portal.portal_caches.clearAllCache()
    self.tic()
    self.portal.ERP5Site_reindexAll()
    self.tic()
    self.assertEqual(len(searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['WAAA', 'BOOO'])),
                     0)
    self.assert_(not 'LEFT JOIN' in searchPredicateList(
      order_line,
      portal_type='Sale Supply Line',
      tested_base_category_list=['WAAA', 'BOOO'],
      src__=1))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestDomainTool))
  return suite

