# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import reindex
from Products.ERP5Type.tests.utils import SubcontentReindexingWrapper
from DateTime import DateTime
import transaction

class TestSupplyMixin:
  def getBusinessTemplateList(self):
    """
      List of needed Business Templates
    """
    return ('erp5_base', 'erp5_pdm', 'erp5_dummy_movement', 'erp5_simulation', 'erp5_trade')

  def afterSetUp(self):
    self.login()
    self.category_tool = self.getCategoryTool()
    self.domain_tool = self.getDomainTool()
    self.catalog_tool = self.getCatalogTool()

    if not hasattr(self.portal, 'testing_folder'):
      self.portal.newContent(portal_type='Folder',
                            id='testing_folder')
    self.folder = self.portal.testing_folder
    self.setUpPreferences()

  def setUpPreferences(self):
    portal_preferences = self.getPreferenceTool()
    preference = getattr(portal_preferences, 'test_system_preference', None)
    if preference is None:
      preference = portal_preferences.newContent(
                      portal_type='System Preference',
                      title='System Preference',
                      id='test_system_preference')
    if preference.getPreferenceState() == 'disabled':
      preference.enable()
    self.tic()


  def beforeTearDown(self):
    module = self.portal.getDefaultModule(self.supply_portal_type)
    module.manage_delObjects(list(module.objectIds()))
    self.tic()

class TestSaleSupply(TestSupplyMixin, SubcontentReindexingWrapper,
    ERP5TypeTestCase):
  """
    Test Supplies usage
  """

  supply_portal_type = 'Sale Supply'
  supply_line_portal_type = 'Sale Supply Line'
  supply_cell_portal_type = 'Sale Supply Cell'
  generic_supply_line_portal_type = 'Supply Line'
  generic_supply_cell_portal_type = 'Supply Cell'
  predicate_portal_type = 'Predicate'
  delivery_portal_type = 'Sale Order'
  movement_portal_type = 'Sale Order Line'

  @reindex
  def _makeMovement(self, **kw):
    """Creates a movement.
    """
    mvt = self.folder.newContent(portal_type='Dummy Movement')
    mvt.edit(**kw)
    return mvt

  @reindex
  def _makeRealMovement(self, **kw):
    """Creates a real movement.
    """
    mvt = self.portal \
      .getDefaultModule(portal_type=self.delivery_portal_type) \
      .newContent(portal_type=self.delivery_portal_type) \
      .newContent(portal_type=self.movement_portal_type)
    mvt.edit(**kw)
    return mvt


  @reindex
  def _makeSupply(self, **kw):
    """Creates a supply.
    """
    if 'portal_type' in kw:
      portal_type = kw.pop('portal_type')
    else:
      portal_type = self.supply_portal_type
    supply = self.portal \
      .getDefaultModule(portal_type=portal_type) \
      .newContent(portal_type=portal_type)
    supply.edit(**kw)
    return supply

  @reindex
  def _makeSupplyLine(self, supply, **kw):
    """Creates a supply line.
    """
    if 'portal_type' in kw:
      portal_type = kw.pop('portal_type')
    else:
      portal_type = self.supply_line_portal_type
    supply_line = supply.newContent(portal_type=portal_type)
    supply_line.edit(**kw)
    return supply_line

  @reindex
  def _makeSupplyCell(self, supply_line, **kw):
    """Creates a supply cell.
    """
    supply_cell = supply_line.newContent(portal_type=self.supply_cell_portal_type)
    supply_cell.edit(**kw)
    return supply_cell

  def _makeSections(self):
    """ make organisations """
    self._makeOrganisation('my_section')
    self._makeOrganisation('your_section')
    self.tic()

  def _makeOrganisation(self, organisation_id):
    """ make an organisation with the id"""
    organisation_module = self.portal.organisation_module
    if getattr(organisation_module, organisation_id, None) is None:
      organisation_module.newContent(portal_type='Organisation',
                                     id=organisation_id)

  def _makeResource(self, resouce_id):
    """ make a resource with the id"""
    product_module = self.portal.product_module
    if getattr(product_module, resouce_id, None) is None:
      product_module.newContent(portal_type="Product",
                                id=resouce_id)
  @reindex
  def _makeVariableSupplyLine(self,
                              supply_portal_type=None,
                              supply_line_portal_type=None,
                              resource_value=None,
                              source_section_value=None,
                              destination_section_value=None,
                              price=None):
    """ Make a supply line with the parameters. """
    supply = self._makeSupply(
      start_date_range_min='2014/01/01',
      start_date_range_max='2014/01/31',
      portal_type=supply_portal_type,
      source_section_value=source_section_value,
      destination_section_value=destination_section_value,
    )
    supply.validate()
    supply_line = self._makeSupplyLine(supply,
                                       portal_type=supply_line_portal_type)
    supply_line.edit(resource_value=resource_value,
                     base_price=price)

    self.tic()


  def _clearCache(self):
    """ Clear cache to test preferences.
    """
    self.portal.portal_caches.clearCache(
      cache_factory_list=('erp5_ui_short', # for preference cache
                          ))


  def test_MovementAndSupplyModification(self):
    """
      Check that moving timeframe of supply
      and then setting movement into that timeframe works.
    """

    # movement is in middle of timeframe...
    movement = self._makeMovement(start_date='2009/01/15')

    supply = self._makeSupply(start_date_range_min='2009/01/01',
                              start_date_range_max='2009/01/31')
    supply.validate()

    supply_line = self._makeSupplyLine(supply)
    supply_cell = self._makeSupplyCell(supply_line)
    self.tic()

    res_line = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_line_portal_type)
    res_cell = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_cell_portal_type)

    # ...and predicate shall be found
    self.assertSameSet(res_line, [supply_line])
    self.assertSameSet(res_cell, [supply_cell])

    # timeframe is moved out of movement date...
    supply.edit(start_date_range_min='2009/02/01',
                start_date_range_max='2009/02/28')

    self.tic()

    res_line = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_line_portal_type)
    res_cell = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_cell_portal_type)

    # ...and predicate shall NOT be found
    self.assertSameSet(res_line, [])
    self.assertSameSet(res_cell, [])

    # movement is going back into timeframe...
    movement.edit(start_date='2009/02/15')

    self.tic()

    res_line = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_line_portal_type)
    res_cell = self.domain_tool.searchPredicateList(movement,
                                                    portal_type=self.supply_cell_portal_type)

    # ...and predicate shall be found
    self.assertSameSet(res_line, [supply_line])
    self.assertSameSet(res_cell, [supply_cell])

  def test_checkLineIsReindexedOnSupplyChange(self):
    """
      Check that Supply Line is properly reindexed (in predicate table)
      when date is changed on Supply.
    """
    original_date = DateTime().earliestTime() # lower precision of date
    new_date = DateTime(original_date + 10)

    self.assertNotEquals(original_date, new_date)

    supply = self._makeSupply(start_date_range_min=original_date)
    supply.validate()
    supply_line = self._makeSupplyLine(supply)

    kw = {
      'predicate.uid': supply_line.getUid(),
      'select_dict': {
        'start_date_range_min': 'predicate.start_date_range_min',
      },
    }

    # check supply line in predicate table
    result = self.catalog_tool(**kw)
    self.assertEqual(1, len(result) )
    result = result[0]
    self.assertEqual(result.start_date_range_min, original_date.toZone('UTC'))

    # set new date on supply...
    supply.edit(start_date_range_min=new_date)
    self.tic()

    # ...and check supply line
    result = self.catalog_tool(**kw)
    self.assertEqual(1, len(result) )
    result = result[0]
    self.assertEqual(result.start_date_range_min, new_date.toZone('UTC'))


  def test_SupplyLineApplied(self):
    """
      Test supply line being found.
      XXX: This tests fails for second run due to bug #1248.
    """
    portal = self.portal
    original_date = DateTime().earliestTime()

    supply = self._makeSupply(start_date_range_min=original_date)
    supply.validate()
    supply_line = self._makeSupplyLine(supply)
    self.tic()

    # create Sale Order and check Supply Line settings when
    # a Resource is set on Sale Order Line
    product = portal.product_module.newContent(portal_type="Product",
                                               title = "Product 1")
    sale_order = portal.sale_order_module.newContent(portal_type = 'Sale Order',
                                                     start_date = DateTime())
    sale_order_line = sale_order.newContent(portal_type = 'Sale Order Line')
    sale_order_line.setResource(product.getRelativeUrl())
    self.tic()
    supply_line_list = self.domain_tool.searchPredicateList(sale_order,
                                      portal_type=self.supply_line_portal_type)
    self.assertSameSet([supply_line], supply_line_list)

  def test_sourceDestinationReferenceOnSupplyLine(self):
    """
      Check that it's possible to set and get a source/destination_reference on
      supply_line
    """
    supply = self._makeSupply(start_date_range_min=DateTime())
    supply.validate()
    supply_line = self._makeSupplyLine(supply)
    supply_line.setSourceReference('my_source_reference')
    self.assertEqual(supply_line.getSourceReference(), 'my_source_reference')
    supply_line.setDestinationReference('my_destination_reference')
    self.assertEqual(supply_line.getDestinationReference(), 'my_destination_reference')

  def test_subcontent_reindexing_supply(self):
    """Tests, that modification on Supply are propagated to children"""
    supply = self.portal.getDefaultModule(self.supply_portal_type).newContent(
                              portal_type=self.supply_portal_type)
    supply_line = supply.newContent(portal_type=self.supply_line_portal_type)
    supply_cell = supply_line.newContent(
        portal_type=self.supply_cell_portal_type)
    supply_line_predicate = supply_line.newContent(
        portal_type=self.predicate_portal_type)

    generic_supply_line = supply.newContent(
        portal_type=self.generic_supply_line_portal_type)
    generic_supply_cell = generic_supply_line.newContent(
        portal_type=self.generic_supply_cell_portal_type)
    generic_supply_predicate = generic_supply_line.newContent(
        portal_type=self.predicate_portal_type)

    self._testSubContentReindexing(supply, [supply_line, supply_cell,
      supply_line_predicate, generic_supply_line, generic_supply_cell, generic_supply_predicate])

  def test_subcontent_reindexing_supply_line(self):
    """Tests, that modification on Supply Line are propagated to children"""
    supply = self.portal.getDefaultModule(self.supply_portal_type).newContent(
                              portal_type=self.supply_portal_type)
    supply_line = supply.newContent(portal_type=self.supply_line_portal_type)
    supply_cell = supply_line.newContent(
        portal_type=self.supply_cell_portal_type)
    supply_line_predicate = supply_line.newContent(
        portal_type=self.predicate_portal_type)

    generic_supply_line = supply.newContent(
        portal_type=self.generic_supply_line_portal_type)
    generic_supply_cell = generic_supply_line.newContent(
        portal_type=self.generic_supply_cell_portal_type)
    generic_supply_predicate = generic_supply_line.newContent(
        portal_type=self.predicate_portal_type)

    self._testSubContentReindexing(supply_line, [supply_cell,
      supply_line_predicate])

    self._testSubContentReindexing(generic_supply_line, [generic_supply_cell,
      generic_supply_predicate])

  def testSupplyCellPropertyAndAccessor(self):
    """
      Check that getter/setter and get/setProperty methods works the same
      on supply cell. This test is added due to a bug introduced by revision
      39918 of ERP5/Document/MappedValue.py.
    """
    supply = self._makeSupply()
    supply_line = self._makeSupplyLine(supply)
    supply_cell = self._makeSupplyCell(supply_line)

    # User uses matrixbox to enter cells(variated data) and
    # it uses mapped value and setProperty method. Catalog uses
    # getter method to index cells.
    supply_cell.setMappedValuePropertyList(
      ['description', 'destination_reference'])

    # test description property
    self.assertEqual(supply_cell.getDescription(None), None)
    self.assertEqual(supply_cell.getProperty('description', None), None)
    supply_cell.setDescription('apple')
    self.assertEqual(supply_cell.getDescription(), 'apple')
    self.assertEqual(supply_cell.getProperty('description'), 'apple')
    supply_cell.setProperty('description', 'lemon')
    self.assertEqual(supply_cell.getDescription(), 'lemon')
    self.assertEqual(supply_cell.getProperty('description'), 'lemon')

    self.tic()

    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), description='apple')), 0)
    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), description='lemon')), 1)

    # test destination_reference property which defines storage_id on
    # property sheet
    self.assertEqual(supply_cell.getDestinationReference(None), None)
    self.assertEqual(supply_cell.getProperty('destination_reference', None), None)
    supply_cell.setDestinationReference('orange')
    self.assertEqual(supply_cell.getDestinationReference(), 'orange')
    self.assertEqual(supply_cell.getProperty('destination_reference'), 'orange')
    supply_cell.setProperty('destination_reference', 'banana')
    self.assertEqual(supply_cell.getDestinationReference(), 'banana')
    self.assertEqual(supply_cell.getProperty('destination_reference'), 'banana')

    self.tic()

    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), destination_reference='orange')), 0)
    self.assertEqual(len(self.portal.portal_catalog(uid=supply_cell.getUid(), destination_reference='banana')), 1)

  def test_getBaseUnitPrice(self):
    currency = self.portal.currency_module.newContent(
      portal_type='Currency',
      base_unit_quantity=0.01)
    product = self.portal.product_module.newContent(portal_type="Product",
                                                    title=self.id())
    supply = self._makeSupply()
    supply.validate()
    supply_line = self._makeSupplyLine(supply, resource_value=product)
    another_supply_line = self._makeSupplyLine(supply, resource_value=product)

    # A new supply line has no no base unit price
    self.assertEqual(None, supply_line.getBaseUnitPrice())

    movement = self.portal.sale_order_module.newContent(
        portal_type='Sale Order',
      ).newContent(
        portal_type='Sale Order Line',
        resource_value=product)

    # A new movement has no no base unit price
    self.assertEqual(None, movement.getBaseUnitPrice())

    # When a price currency is set, the price precision uses the precision from
    # price currency
    movement.setPriceCurrencyValue(currency)
    self.tic()

    self.assertEqual(None, movement.getBaseUnitPrice())
    self.assertEqual(2, movement.getPricePrecision())

    # If base unit price is set on an applicable supply line, then the base
    # unit price of this movement will use the one from the supply line
    supply_line.setBaseUnitPrice(0.001)
    self.assertEqual(3, supply_line.getPricePrecision())
    self.tic()

    self.assertEqual(0.001, movement.getBaseUnitPrice())
    self.assertEqual(3, movement.getPricePrecision())

    # Base unit pice have been copied on the movement
    self.assertTrue(movement.hasBaseUnitPrice())

    # Supply lines does not lookup base unit price from other supply lines
    self.assertEqual(None, another_supply_line.getBaseUnitPrice())


  def testGetPriceWithOptimisation(self):
    """
     Test pricing optimisation based on the preference configuration.
    """
    preference = getattr(self.getPreferenceTool(), 'test_system_preference')
    preference.setPreferredPricingOptimise(False)
    # every time modifying preference, need to clear cache
    self._clearCache()
    self.assertEquals(preference.getPreferredPricingOptimise(), False)
    self._makeSections()
    self._makeResource(self.id())
    self.tic()

    resource_value = self.portal.product_module[self.id()]
    source_section_value = self.portal.organisation_module['my_section']
    destination_section_value = self.portal.organisation_module['your_section']
    movement = self._makeRealMovement(
      start_date='2014/01/15',
      resource_value=resource_value,
      source_section_value=source_section_value,
      destination_section_value=destination_section_value)
    self.assertEquals(movement.getPrice(), None)

    supply = self._makeSupply(
      start_date_range_min='2014/01/01',
      start_date_range_max='2014/01/31',
      source_section_value=source_section_value,
      destination_section_value=destination_section_value,
    )
    supply.validate()
    supply_line = self._makeSupplyLine(supply)
    supply_line.edit(resource_value=resource_value,
                     base_price=100)

    self.tic()

    self.assertEquals(movement.getPrice(), 100)
    # only the flag is enabled, the behavior is same with not-optimised one
    preference.setPreferredPricingOptimise(True)
    preference.getPreferredPricingSupplyPathKeyCategoryList(
      ['resource', 'source_section', 'destination_section'])
    self.tic()
    self._clearCache()
    self.assertEquals(movement.getPrice(), 100)

    # With following setting, Movement_getPriceCalculationOperandDict creates
    # efficient query from the RDBMS point of view.
    # Note that following assertion does not check the efficiency, this only
    # checks that the functionality is kept even after the optimisation.
    preference.setPreferredSaleMovementSupplyPathTypeList(
      ['Sale Supply Line'])
    preference.setPreferredPurchaseMovementSupplyPathTypeList(
      ['Purchase Supply Line'])
    preference.setPreferredInternalMovementSupplyPathTypeList(
      ['Internal Supply Line'])
    self.tic()
    self._clearCache()

    movement.setPrice(None) # getPrice() sets the price, so clear it first.
    self.assertEquals(movement.getPrice(), 100)
    preference.setPreferredPricingOptimise(False)
    self._clearCache()

  def test_getPriceWithOptimisationWrongSetting(self):
    """
     Check Pricing optimisation with a strange setting.

     With the setting, the strange supply path will be selected, thus
     the following assertion make sure the preference certainly works.
    """
    preference = getattr(self.getPreferenceTool(), 'test_system_preference')
    preference.setPreferredPricingOptimise(True)
    self._clearCache()
    self.assertEquals(preference.getPreferredPricingOptimise(), True)
    self._makeSections()
    self._makeResource(self.id())
    self.tic()

    resource_value = self.portal.product_module[self.id()]
    source_section_value = self.portal.organisation_module['my_section']
    destination_section_value = self.portal.organisation_module['your_section']
    self.tic()
    preference.getPreferredPricingSupplyPathKeyCategoryList(
      ['resource', 'source_section', 'destination_section'])

    movement = self._makeRealMovement(
      start_date='2014/01/15',
      resource_value=resource_value,
      source_section_value=source_section_value,
      destination_section_value=destination_section_value)
    self._makeVariableSupplyLine(supply_portal_type='Sale Supply',
                                 supply_line_portal_type='Sale Supply Line',
                                 source_section_value=source_section_value,
                                 destination_section_value=destination_section_value,
                                 resource_value=resource_value,
                                 price=5)
    self._makeVariableSupplyLine(supply_portal_type='Purchase Supply',
                                 supply_line_portal_type='Purchase Supply Line',
                                 source_section_value=source_section_value,
                                 destination_section_value=destination_section_value,
                                 resource_value=resource_value,
                                 price=10)
    self._makeVariableSupplyLine(supply_portal_type='Internal Supply',
                                 supply_line_portal_type='Internal Supply Line',
                                 resource_value=resource_value,
                                 source_section_value=source_section_value,
                                 destination_section_value=destination_section_value,
                                 price=15)
    self.tic()
    # wrong setting, then proper supply path can not be found, select wrong one
    if self.delivery_portal_type == 'Sale Order':
      preference.setPreferredSaleMovementSupplyPathTypeList([
        'Purchase Supply Line'])
      self._clearCache()
      self.tic()
      movement.setPrice(None)
      self.assertEquals(movement.getPrice(), 10)
    elif self.delivery_portal_type in ('Purchase Order', 'Internal Order'):
      preference.setPreferredPurchaseMovementSupplyPathTypeList(
        ['Sale Supply Line'])
      preference.setPreferredInternalMovementSupplyPathTypeList(
        ['Sale Supply Line'])
      self._clearCache()
      self.tic()
      movement.setPrice(None)
      self.assertEquals(movement.getPrice(), 5)
    preference.setPreferredPricingOptimise(False)
    self._clearCache()

  def test_getPriceDoesNotLookupPriceDuringEdit(self):
    """Test getPrice does not lookup price during edit.
    """
    movement = self._makeRealMovement()

    def methodThatShouldNotBeCalled(*args, **kw):
      self.fail("price lookup should not happen")
    movement.getPriceCalculationOperandDict = methodThatShouldNotBeCalled
    movement._getPrice = methodThatShouldNotBeCalled

    movement.edit(price=10)
    self.assertEqual(10, movement.getPrice())
    self.abort()

class TestPurchaseSupply(TestSaleSupply):
  """
    Test Purchase Supplies usage
  """
  supply_portal_type = 'Purchase Supply'
  supply_line_portal_type = 'Purchase Supply Line'
  supply_cell_portal_type = 'Purchase Supply Cell'
  delivery_portal_type = 'Purchase Order'
  movement_portal_type = 'Purchase Order Line'


class TestInternalSupply(TestSaleSupply):
  """
    Test Internal Supplies usage
  """
  supply_portal_type = 'Internal Supply'
  supply_line_portal_type = 'Internal Supply Line'
  supply_cell_portal_type = 'Internal Supply Cell'
  delivery_portal_type = 'Internal Order'
  movement_portal_type = 'Internal Order Line'


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestSaleSupply))
  suite.addTest(unittest.makeSuite(TestPurchaseSupply))
  suite.addTest(unittest.makeSuite(TestInternalSupply))
  return suite
