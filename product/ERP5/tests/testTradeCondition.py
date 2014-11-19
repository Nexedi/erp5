##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Jerome Perrin <jerome@nexedi.com>
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

from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5Type.tests.utils import SubcontentReindexingWrapper

class TradeConditionTestCase(ERP5TypeTestCase, SubcontentReindexingWrapper):

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade',
            'erp5_accounting', 'erp5_invoicing', 'erp5_simplified_invoicing')

  size_category_list = ['small', 'big']
  def afterSetUp(self):
    for category_id in self.size_category_list:
      self.portal.portal_categories.size.newContent(id=category_id,
                                                    title=category_id)
    self.base_amount = self.portal.portal_categories.base_amount
    self.client = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    title='Client')
    self.vendor = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    title='Vendor')
    self.resource = self.portal.product_module.newContent(
                                    portal_type='Product',
                                    title='Resource')
    self.variated_resource = self.portal.product_module.newContent(
                                    portal_type='Product',
                                    title='Variated Resource',
                                    variation_base_category_list=['size'],
                                    variation_category_list=['size/small',
                                                             'size/big'])
    self.currency = self.portal.currency_module.newContent(
                                    portal_type='Currency',
                                    title='Currency')
    self.trade_condition_module = self.portal.getDefaultModule(
                                      self.trade_condition_type)
    self.trade_condition = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition_type,
                            title='Trade Condition')
    self.trade_condition.validate()
    self.order_module = self.portal.getDefaultModule(
                                      self.order_type)
    self.order = self.order_module.newContent(
                            portal_type=self.order_type,
                            created_by_builder=1,
                            title='Order')

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.organisation_module,
                   self.portal.currency_module,
                   self.portal.product_module,
                   self.trade_condition_module,
                   self.order_module,
                   self.portal.portal_categories.base_amount,
                   self.portal.portal_categories.size,
      ):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()

  def test_subcontent_supply_line_reindexing(self):
    trade_condition = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition_type)
    supply_line = trade_condition.newContent(portal_type=self.supply_line_type)
    self._testSubContentReindexing(trade_condition, [supply_line])

class TestApplyTradeCondition(TradeConditionTestCase):
  """Tests Applying Trade Conditions
  """
  def test_apply_trade_condition_set_categories(self):
    self.trade_condition.setSourceSectionValue(self.vendor)
    self.trade_condition.setDestinationSectionValue(self.client)
    self.trade_condition.setSourceValue(self.vendor)
    self.trade_condition.setDestinationValue(self.client)
    self.trade_condition.setPriceCurrencyValue(self.currency)
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    self.assertEqual(self.vendor, self.order.getSourceSectionValue())
    self.assertEqual(self.vendor, self.order.getSourceValue())
    self.assertEqual(self.client, self.order.getDestinationSectionValue())
    self.assertEqual(self.client, self.order.getDestinationValue())
    self.assertEqual(self.currency, self.order.getPriceCurrencyValue())

  def test_apply_trade_condition_keep_categories(self):
    # source section & source are set on the order, not on the TC
    self.order.setSourceSectionValue(self.vendor)
    self.order.setSourceValue(self.vendor)

    self.trade_condition.setSourceSectionValue(None)
    self.trade_condition.setSourceValue(None)
    self.trade_condition.setDestinationSectionValue(self.client)
    self.trade_condition.setDestinationValue(self.client)
    self.trade_condition.setPriceCurrencyValue(self.currency)
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # Applying the TC keeps values on the order
    self.assertEqual(self.vendor, self.order.getSourceSectionValue())
    self.assertEqual(self.vendor, self.order.getSourceValue())
    self.assertEqual(self.client, self.order.getDestinationSectionValue())
    self.assertEqual(self.client, self.order.getDestinationValue())
    self.assertEqual(self.currency, self.order.getPriceCurrencyValue())

  def test_apply_trade_condition_set_categories_with_hierarchy(self):
    trade_condition_source = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition.getPortalType(),
                            title='Trade Condition Source',
                            source_value=self.vendor,
                            source_section_value=self.vendor)
    trade_condition_dest = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition.getPortalType(),
                            title='Trade Condition Destination',
                            destination_value=self.client,
                            destination_section_value=self.client,
                            price_currency_value=self.currency,
                            # also set a source, it should not be used
                            source_value=self.client)
    self.trade_condition.setSpecialiseValueList(
        (trade_condition_source, trade_condition_dest))

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    self.assertEqual(self.vendor, self.order.getSourceSectionValue())
    self.assertEqual(self.vendor, self.order.getSourceValue())
    self.assertEqual(self.client, self.order.getDestinationSectionValue())
    self.assertEqual(self.client, self.order.getDestinationValue())
    self.assertEqual(self.currency, self.order.getPriceCurrencyValue())

  def test_apply_trade_condition_copy_subobjects(self):
    self.trade_condition.setPaymentConditionTradeDate('custom')
    self.trade_condition.setPaymentConditionPaymentDate(DateTime(2001, 01, 01))
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    
    self.assertEqual('custom', self.order.getPaymentConditionTradeDate())
    self.assertEqual(DateTime(2001, 01, 01),
                      self.order.getPaymentConditionPaymentDate())

  def test_apply_twice_trade_condition_copy_subobjects(self):
    self.trade_condition.setPaymentConditionTradeDate('custom')
    self.trade_condition.setPaymentConditionPaymentDate(DateTime(2001, 01, 01))
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    self.assertEqual(1, len(self.order.contentValues(
                                portal_type='Payment Condition')))
    self.assertEqual('custom', self.order.getPaymentConditionTradeDate())
    self.assertEqual(DateTime(2001, 01, 01),
                      self.order.getPaymentConditionPaymentDate())
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    self.assertEqual(1, len(self.order.contentValues(
                                portal_type='Payment Condition')))

  def test_apply_trade_condition_copy_subobjects_with_hierarchy(self):
    other_trade_condition = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition.getPortalType(),
                            title='Other Trade Condition')
    other_trade_condition.setPaymentConditionTradeDate('custom')
    other_trade_condition.setPaymentConditionPaymentDate(
                                              DateTime(2001, 01, 01))

    self.trade_condition.setSpecialiseValue(other_trade_condition)
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    
    self.assertEqual('custom', self.order.getPaymentConditionTradeDate())
    self.assertEqual(DateTime(2001, 01, 01),
                      self.order.getPaymentConditionPaymentDate())

  def test_apply_trade_condition_twice_update_order(self):
    self.trade_condition.setSourceSectionValue(self.vendor)
    self.trade_condition.setDestinationSectionValue(self.client)
    self.trade_condition.setSourceValue(self.vendor)
    self.trade_condition.setDestinationValue(self.client)
    self.trade_condition.setPriceCurrencyValue(self.currency)
    self.trade_condition.setPaymentConditionTradeDate('custom')
    self.trade_condition.setPaymentConditionPaymentDate(DateTime(2001, 01, 01))
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    self.tic()

    self.assertEqual(self.vendor, self.order.getSourceSectionValue())
    self.assertEqual(self.vendor, self.order.getSourceValue())
    self.assertEqual(self.client, self.order.getDestinationSectionValue())
    self.assertEqual(self.client, self.order.getDestinationValue())
    self.assertEqual(self.currency, self.order.getPriceCurrencyValue())
    self.assertEqual('custom', self.order.getPaymentConditionTradeDate())
    self.assertEqual(DateTime(2001, 01, 01),
                      self.order.getPaymentConditionPaymentDate())

    new_vendor = self.portal.organisation_module.newContent(
                    portal_type='Organisation',
                    title='New vendor')
    new_trade_condition = self.trade_condition_module.newContent(
                    portal_type=self.trade_condition_type,
                    source_section_value=new_vendor,
                    payment_condition_trade_date='custom',
                    payment_condition_payment_date=DateTime(2002, 2, 2))

    self.order.Order_applyTradeCondition(new_trade_condition, force=1)
    self.assertEqual(new_vendor, self.order.getSourceSectionValue())
    self.assertEqual(self.vendor, self.order.getSourceValue())
    self.assertEqual(self.client, self.order.getDestinationSectionValue())
    self.assertEqual(self.client, self.order.getDestinationValue())
    self.assertEqual(self.currency, self.order.getPriceCurrencyValue())
    self.assertEqual('custom', self.order.getPaymentConditionTradeDate())
    self.assertEqual(DateTime(2002, 02, 02),
                      self.order.getPaymentConditionPaymentDate())


class TestTradeConditionSupplyLine(TradeConditionTestCase):
  """A trade condition can contain supply line and those supply lines are used
  in priority, for example to calculate the price
  """
  def test_category_acquisition(self):
    self.trade_condition.setSourceValue(self.vendor)
    self.trade_condition.setSourceSectionValue(self.vendor)
    self.trade_condition.setDestinationValue(self.client)
    self.trade_condition.setDestinationSectionValue(self.client)
    self.trade_condition.setPriceCurrencyValue(self.currency)

    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type)

    self.assertEqual(self.vendor, supply_line.getSourceValue())
    self.assertEqual(self.vendor, supply_line.getSourceSectionValue())
    self.assertEqual(self.client, supply_line.getDestinationValue())
    self.assertEqual(self.client, supply_line.getDestinationSectionValue())
    self.assertEqual(self.currency, supply_line.getPriceCurrencyValue())

  def test_movement_price_assignment(self):
    # supply line from the trade condition apply to the movements in order
    # where this trade condition is used
    #
    # Order ---> TC (123)
    #
    # price should be 123
    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.resource,
                                    base_price=123)

    self.order.setSpecialiseValue(self.trade_condition)
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    self.assertEqual(123, line.getPrice())

    # supply line in the direct trade condition should have priority
    # than its specialised trade condition
    #
    # Order ---> TC (125) ---> TC (123)
    #
    # price should be 125
    trade_condition2 = self.trade_condition_module.newContent(
      portal_type=self.trade_condition_type,
      specialise_value=self.trade_condition)
    trade_condition2.validate()
    trade_condition2.newContent(
      portal_type=self.supply_line_type,
      resource_value=self.resource,
      base_price=125)
    self.order.setSpecialiseValue(trade_condition2)
    self.tic()
    line.setPrice(None)
    self.assertEqual(125, line.getPrice())

    # supply line in the first direct trade condition should have
    # priority than the second trade condition
    #
    # Order -+-> TC (127)
    #        +-> TC (125) ---> TC (123)
    #
    # price should be 127
    #
    # Order -+-> TC (125) ---> TC (123)
    #        +-> TC (127)
    #
    # price should be 125
    trade_condition3 = self.trade_condition_module.newContent(
      portal_type=self.trade_condition_type)
    trade_condition3.validate()
    trade_condition3.newContent(
      portal_type=self.supply_line_type,
      resource_value=self.resource,
      base_price=127)
    self.order.setSpecialiseValueList((trade_condition3, trade_condition2))
    self.tic()
    line.setPrice(None)
    self.assertEqual(127, line.getPrice())
    self.order.setSpecialiseValueList((trade_condition2, trade_condition3))
    self.tic()
    line.setPrice(None)
    self.assertEqual(125, line.getPrice())

    # supply line in the second direct trade condition should have
    # priority than the first trade condition's specialised trade
    # condition
    #
    # Order -+-> TC (---) ---> TC (123)
    #        +-> TC (127)
    #
    # price should be 127
    #
    # Order -+-> TC (127)
    #        +-> TC (---) ---> TC (123)
    #
    # price should be 127
    trade_condition4 = self.trade_condition_module.newContent(
      portal_type=self.trade_condition_type,
      specialise_value=self.trade_condition)
    trade_condition4.validate()
    self.order.setSpecialiseValueList((trade_condition4, trade_condition3))
    self.tic()
    line.setPrice(None)
    self.assertEqual(127, line.getPrice())
    self.order.setSpecialiseValueList((trade_condition3, trade_condition4))
    self.tic()
    line.setPrice(None)
    self.assertEqual(127, line.getPrice())

  def test_supply_line_priority(self):
    # supply lines from related trade condition should have priority over
    # supply lines from supply modules
    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          source_section_value=self.vendor,
                                          destination_section_value=self.client)
    other_supply.validate()
    other_supply_line = other_supply.newContent(
                                    portal_type=self.supply_line_type,
                                    base_price=1)
    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.resource,
                                    base_price=2)
    self.order.setSpecialiseValue(self.trade_condition)
    self.order.setSourceSectionValue(self.vendor)
    self.order.setDestinationSectionValue(self.vendor)
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    # using the supply line inside trade condition
    self.assertEqual(2, line.getPrice())

  def test_supply_cell_priority(self):
    # supply lines from related trade condition should have priority over
    # supply cells from supply modules
    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          source_section_value=self.vendor,
                                          destination_section_value=self.client)
    other_supply.validate()
    other_supply_line = other_supply.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.variated_resource)
    other_supply_line.setPVariationBaseCategoryList(['size'])
    other_supply_line.updateCellRange(base_id='path')
    self.tic()
    other_small_cell = other_supply_line.newCell(base_id='path', *['size/small'])
    other_small_cell.setMappedValuePropertyList(['base_price'])
    other_small_cell.setVariationCategoryList(['size/small'])
    other_small_cell.setMembershipCriterionBaseCategoryList(['size'])
    other_small_cell.setMembershipCriterionCategoryList(['size/small'])
    other_small_cell.setBasePrice(1)

    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.variated_resource,)
    supply_line.setPVariationBaseCategoryList(['size'])
    supply_line.updateCellRange(base_id='path')
    self.tic()

    small_cell = supply_line.newCell(base_id='path', *['size/small'])
    small_cell.setMappedValuePropertyList(['base_price'])
    small_cell.setVariationCategoryList(['size/small'])
    small_cell.setMembershipCriterionBaseCategoryList(['size'])
    small_cell.setMembershipCriterionCategoryList(['size/small'])
    small_cell.setBasePrice(2)

    self.order.setSpecialiseValue(self.trade_condition)
    self.order.setSourceSectionValue(self.vendor)
    self.order.setDestinationSectionValue(self.client)
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.variated_resource,)
    self.assertEqual(None, line.getPrice())
    line.setVariationBaseCategoryList(['size'])
    line.setVariationCategoryList(['size/small'])
    line.updateCellRange(base_id='movement')
    self.tic()

    cell = line.newCell(base_id='movement', *['size/small'])
    cell.setQuantity(1)
    self.assertEqual(2, cell.getPrice())

  def test_supply_line_in_invalidated_trade_condition_does_not_apply(self):
    # supply lines from supply modules
    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          source_section_value=self.vendor,
                                          destination_section_value=self.client)
    other_supply.validate()
    other_supply_line = other_supply.newContent(
                                    portal_type=self.supply_line_type,
                                    base_price=1)
    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.resource,
                                    base_price=2)
    self.order.setSpecialiseValue(self.trade_condition)
    self.order.setSourceSectionValue(self.vendor)
    self.order.setDestinationSectionValue(self.client)

    self.trade_condition.invalidate()
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    # not using the supply line inside trade condition
    self.assertEqual(1, line.getPrice())

  def test_supply_line_in_invalidated_trade_condition_with_reference_does_not_apply(self):
    # edge case derived from
    # test_supply_line_in_invalidated_trade_condition_does_not_apply, if a
    # trade condition have a reference and is invalidated, composition
    # mechanism will lookup another applicable trade condition, which can fail,
    # but this should not affect getPrice
    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          source_section_value=self.vendor,
                                          destination_section_value=self.client)
    other_supply.validate()
    other_supply_line = other_supply.newContent(
                                    portal_type=self.supply_line_type,
                                    base_price=1)
    self.trade_condition.setReference(self.id())
    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.resource,
                                    base_price=2)
    self.order.setSpecialiseValue(self.trade_condition)
    self.order.setSourceSectionValue(self.vendor)
    self.order.setDestinationSectionValue(self.client)

    self.trade_condition.invalidate()
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    # not using the supply line inside trade condition
    self.assertEqual(1, line.getPrice())

  def test_supply_line_in_other_trade_condition_does_not_apply(self):
    """Supply lines from trade condition not related to an order does not apply.
    """
    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.resource,
                                    base_price=2)
    self.assertEqual(None, self.order.getSpecialiseValue())
    self.order.setSourceSectionValue(self.vendor)
    self.order.setDestinationSectionValue(self.client)

    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    # not using the supply line inside trade condition
    self.assertEqual(None, line.getPrice())

  # TODO: move to testSupplyLine ! (which does not exist yet)
  def test_supply_line_section(self):
    # if a supply lines defines a section, it has priority over supply lines
    # not defining sections
    other_entity = self.portal.organisation_module.newContent(
                                      portal_type='Organisation',
                                      title='Other')
    supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,)
    supply.validate()
    supply_line = supply.newContent(
                                    portal_type=self.supply_line_type,
                                    base_price=1)

    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          destination_section_value=self.client,
                                          source_section_value=self.vendor)
    other_supply.validate()
    other_supply_line = other_supply.newContent(
                                    portal_type=self.supply_line_type,
                                    base_price=2)

    self.order.setSourceSectionValue(self.vendor)
    self.order.setDestinationSectionValue(self.client)
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    # using the supply line with section defined
    self.assertEqual(2, line.getPrice())


class TestEffectiveTradeCondition(TradeConditionTestCase):
  """Tests for getEffectiveModel

  XXX open questions:
   - should getEffectiveModel take validation state into account ? if yes, how
     to do it in generic/customizable way ?
   - would getEffectiveModel(at_date) be enough ?
  """
  def test_getEffectiveModel(self):
    # getEffectiveModel returns the model with highest version
    reference = self.id()
    self.trade_condition.setReference(reference)
    self.trade_condition.setVersion('001')
    self.trade_condition.setEffectiveDate('2009/01/01')
    self.trade_condition.setExpirationDate('2009/12/31')
    other_trade_condition = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition.getPortalType(),
                            title='Other Trade Condition',
                            reference=reference,
                            effective_date='2009/01/01',
                            expiration_date='2009/12/31',
                            version='002')
    self.tic()

    self.assertEqual(other_trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

    # outside date range: should it raise or return nothing ?
    self.assertRaises(Exception,
        self.trade_condition.getEffectiveModel,
                    start_date=DateTime('2008/06/01'),
                    stop_date=DateTime('2008/06/01'))
    self.assertRaises(Exception,
        self.trade_condition.getEffectiveModel,
                    start_date=DateTime('2010/06/01'),
                    stop_date=DateTime('2010/06/01'))

  def test_getEffectiveModel_return_self(self):
    # getEffectiveModel returns the trade condition if it's effective
    self.trade_condition.setReference(self.id())
    self.trade_condition.setEffectiveDate('2009/01/01')
    self.trade_condition.setExpirationDate('2009/12/31')
    self.tic()
    self.assertEqual(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

  def test_getEffectiveModel_without_dates(self):
    # a trade condition without effective / expiration date is effective
    self.trade_condition.setReference(self.id())
    self.trade_condition.setEffectiveDate(None)
    self.trade_condition.setExpirationDate(None)
    self.tic()
    self.assertEqual(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

    self.trade_condition.setEffectiveDate(None)
    self.trade_condition.setExpirationDate('2009/12/31')
    self.tic()
    self.assertEqual(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

    self.trade_condition.setEffectiveDate('2009/01/01')
    self.trade_condition.setExpirationDate(None)
    self.tic()
    self.assertEqual(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

  def test_getEffectiveModel_return_self_when_no_reference(self):
    # when no reference defined, getEffectiveModel returns the trade condition.
    self.trade_condition.setReference(None)
    self.assertEqual(self.trade_condition,
        self.trade_condition.getEffectiveModel())
    self.assertEqual(self.trade_condition,
        self.trade_condition.getEffectiveModel(start_date=DateTime(),
                                               stop_date=DateTime()))



class TestWithSaleOrder:
  order_type = 'Sale Order'
  order_line_type = 'Sale Order Line'
  order_cell_type = 'Sale Order Cell'
  trade_condition_type = 'Sale Trade Condition'
  supply_type = 'Sale Supply'
  supply_line_type = 'Sale Supply Line'

class TestWithPurchaseOrder:
  order_type = 'Purchase Order'
  order_line_type = 'Purchase Order Line'
  order_cell_type = 'Purchase Order Cell'
  trade_condition_type = 'Purchase Trade Condition'
  supply_type = 'Purchase Supply'
  supply_line_type = 'Purchase Supply Line'

class TestWithSaleInvoice:
  order_type = 'Sale Invoice Transaction'
  order_line_type = 'Invoice Line'
  order_cell_type = 'Invoice Cell'
  trade_condition_type = 'Sale Trade Condition'
  supply_type = 'Sale Supply'
  supply_line_type = 'Sale Supply Line'

class TestWithPurchaseInvoice:
  order_type = 'Purchase Invoice Transaction'
  order_line_type = 'Invoice Line'
  order_cell_type = 'Invoice Cell'
  trade_condition_type = 'Purchase Trade Condition'
  supply_type = 'Purchase Supply'
  supply_line_type = 'Purchase Supply Line'


class TestApplyTradeConditionSaleOrder(
      TestApplyTradeCondition, TestWithSaleOrder):
  pass
class TestApplyTradeConditionPurchaseOrder(
      TestApplyTradeCondition, TestWithPurchaseOrder):
  pass

class TestTradeConditionSupplyLineSaleOrder(
      TestTradeConditionSupplyLine, TestWithSaleOrder):
  pass
class TestTradeConditionSupplyLinePurchaseOrder(
      TestTradeConditionSupplyLine, TestWithPurchaseOrder):
  pass
class TestTradeConditionSupplyLineSaleInvoice(
      TestTradeConditionSupplyLine, TestWithSaleInvoice):
  pass
class TestTradeConditionSupplyLinePurchaseInvoice(
      TestTradeConditionSupplyLine, TestWithPurchaseInvoice):
  pass

class TestEffectiveSaleTradeCondition(
            TestEffectiveTradeCondition,
            TestWithSaleOrder):
  pass
class TestEffectivePurchaseTradeCondition(
            TestEffectiveTradeCondition,
            TestWithPurchaseOrder):
  pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestApplyTradeConditionSaleOrder))
  suite.addTest(unittest.makeSuite(TestApplyTradeConditionPurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLineSaleOrder))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLinePurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLineSaleInvoice))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLinePurchaseInvoice))
  suite.addTest(unittest.makeSuite(TestEffectiveSaleTradeCondition))
  suite.addTest(unittest.makeSuite(TestEffectivePurchaseTradeCondition))
  return suite
