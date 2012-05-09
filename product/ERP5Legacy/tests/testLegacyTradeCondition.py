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

class TradeConditionTestCase(ERP5TypeTestCase):
  """Tests for Trade Conditions and Tax
  """
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_simulation', 'erp5_simulation_legacy',
            'erp5_pdm', 'erp5_trade', 'erp5_accounting',
            'erp5_invoicing', 'erp5_tax_resource', 'erp5_discount_resource',
            'erp5_legacy_tax_system', 'erp5_simplified_invoicing',
            'erp5_trade_simulation_legacy',
            'erp5_accounting_simulation_legacy',
            'erp5_invoicing_simulation_legacy')

  def validateRules(self):
    """
    try to validate all rules in rule_tool.
    """
    rule_tool = self.getRuleTool()
    for rule in rule_tool.contentValues(
        portal_type=rule_tool.getPortalRuleTypeList()):
      if rule.getValidationState() != 'validated':
        rule.validate()
      # do not use new 'XXX Simulation Rule' in legacy tests.
      if 'Simulation Rule' in rule.getPortalType():
        rule.invalidate()

  size_category_list = ['small', 'big']
  def afterSetUp(self):
    self.validateRules()
    for category_id in self.size_category_list:
      self.portal.portal_categories.size.newContent(id=category_id,
                                                    title=category_id)
    self.base_amount = self.portal.portal_categories.base_amount
    self.tax = self.portal.tax_module.newContent(
                                    portal_type='Tax',
                                    title='Tax')
    self.discount = self.portal.discount_module.newContent(
                                    portal_type='Discount',
                                    title='Discount')
    self.client = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    title='Client')
    self.vendor = self.portal.organisation_module.newContent(
                                    portal_type='Organisation',
                                    title='Vendor')
    self.resource = self.portal.product_module.newContent(
                                    portal_type='Product',
                                    title='Resource')
    self.currency = self.portal.currency_module.newContent(
                                    portal_type='Currency',
                                    title='Currency')
    self.trade_condition_module = self.portal.getDefaultModule(
                                      self.trade_condition_type)
    self.trade_condition = self.trade_condition_module.newContent(
                            portal_type=self.trade_condition_type,
                            title='Trade Condition')
    self.order_module = self.portal.getDefaultModule(
                                      self.order_type)
    self.order = self.order_module.newContent(
                            portal_type=self.order_type,
                            created_by_builder=1,
                            title='Order')

  def beforeTearDown(self):
    self.abort()
    for module in (self.portal.tax_module,
                   self.portal.organisation_module,
                   self.portal.currency_module,
                   self.portal.product_module,
                   self.portal.accounting_module,
                   self.portal.account_module,
                   self.portal.portal_simulation,
                   self.trade_condition_module,
                   self.order_module,
                   self.portal.portal_categories.base_amount,
                   self.portal.portal_categories.size,
      ):
      module.manage_delObjects(list(module.objectIds()))
    self.tic()


class AccountingBuildTestCase(TradeConditionTestCase):
  """Same as TradeConditionTestCase, but with a rule to generate
  accounting.
  """
  def afterSetUp(self):
    TradeConditionTestCase.afterSetUp(self)
    self.receivable_account = self.portal.account_module.newContent(
                                    id='receivable',
                                    title='Receivable',
                                    account_type='asset/receivable')
    self.payable_account = self.portal.account_module.newContent(
                                    id='payable',
                                    title='Payable',
                                    account_type='liability/payable')
    self.income_account = self.portal.account_module.newContent(
                                    id='income',
                                    title='Income',
                                    account_type='income')
    self.expense_account = self.portal.account_module.newContent(
                                    id='expense',
                                    title='Expense',
                                    account_type='expense')
    self.collected_tax_account = self.portal.account_module.newContent(
                                    id='collected_tax',
                                    title='Collected Tax',
                                    account_type='liability/payable/collected_vat')
    self.refundable_tax_account = self.portal.account_module.newContent(
                                    id='refundable_tax',
                                    title='Refundable Tax',
                                    account_type='asset/receivable/refundable_vat')

    for account in self.portal.account_module.contentValues():
      self.assertNotEquals(account.getAccountTypeValue(), None)
      account.validate()
    
    itr = self.portal.portal_rules.newContent(
                        portal_type='Invoice Transaction Rule',
                        reference='default_invoice_transaction_rule',
                        id='test_invoice_transaction_rule',
                        title='Transaction Rule',
                        test_method_id='SimulationMovement_testInvoiceTransactionRule',
                        version=100)
    predicate = itr.newContent(portal_type='Predicate',)
    predicate.edit(
            string_index='resource_type',
            title='Resource Product',
            int_index=1,
            test_method_id='SimulationMovement_isDeliveryMovement' )
    predicate = itr.newContent(portal_type='Predicate')
    predicate.edit(
            string_index='resource_type',
            title='Resource Tax',
            int_index=2,
            test_method_id='SimulationMovement_isTaxMovement' )
    self.tic()
    accounting_rule_cell_list = itr.contentValues(
                            portal_type='Accounting Rule Cell')
    self.assertEquals(2, len(accounting_rule_cell_list))
    product_rule_cell = itr._getOb("movement_0")
    self.assertEquals(product_rule_cell.getTitle(), 'Resource Product')
    product_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.receivable_account,
                         destination_value=self.payable_account,
                         quantity=-1)
    product_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.income_account,
                         destination_value=self.expense_account,
                         quantity=1)
    
    tax_rule_cell = itr._getOb("movement_1")
    self.assertEquals(tax_rule_cell.getTitle(), 'Resource Tax')
    tax_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.receivable_account,
                         destination_value=self.payable_account,
                         quantity=-1)
    tax_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.collected_tax_account,
                         destination_value=self.refundable_tax_account,
                         quantity=1)
    itr.validate()
    self.tic()

  def beforeTearDown(self):
    TradeConditionTestCase.beforeTearDown(self)
    self.portal.portal_rules.manage_delObjects('test_invoice_transaction_rule')
    self.tic()

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
    
    self.assertEquals(self.vendor, self.order.getSourceSectionValue())
    self.assertEquals(self.vendor, self.order.getSourceValue())
    self.assertEquals(self.client, self.order.getDestinationSectionValue())
    self.assertEquals(self.client, self.order.getDestinationValue())
    self.assertEquals(self.currency, self.order.getPriceCurrencyValue())

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
    self.assertEquals(self.vendor, self.order.getSourceSectionValue())
    self.assertEquals(self.vendor, self.order.getSourceValue())
    self.assertEquals(self.client, self.order.getDestinationSectionValue())
    self.assertEquals(self.client, self.order.getDestinationValue())
    self.assertEquals(self.currency, self.order.getPriceCurrencyValue())

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
    
    self.assertEquals(self.vendor, self.order.getSourceSectionValue())
    self.assertEquals(self.vendor, self.order.getSourceValue())
    self.assertEquals(self.client, self.order.getDestinationSectionValue())
    self.assertEquals(self.client, self.order.getDestinationValue())
    self.assertEquals(self.currency, self.order.getPriceCurrencyValue())

  def test_apply_trade_condition_copy_subobjects(self):
    self.trade_condition.setPaymentConditionTradeDate('custom')
    self.trade_condition.setPaymentConditionPaymentDate(DateTime(2001, 01, 01))
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    
    self.assertEquals('custom', self.order.getPaymentConditionTradeDate())
    self.assertEquals(DateTime(2001, 01, 01),
                      self.order.getPaymentConditionPaymentDate())

  def test_apply_twice_trade_condition_copy_subobjects(self):
    self.trade_condition.setPaymentConditionTradeDate('custom')
    self.trade_condition.setPaymentConditionPaymentDate(DateTime(2001, 01, 01))
    self.order.setSpecialiseValue(self.trade_condition)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    self.assertEquals(1, len(self.order.contentValues(
                                portal_type='Payment Condition')))
    self.assertEquals('custom', self.order.getPaymentConditionTradeDate())
    self.assertEquals(DateTime(2001, 01, 01),
                      self.order.getPaymentConditionPaymentDate())
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    self.assertEquals(1, len(self.order.contentValues(
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
    
    self.assertEquals('custom', self.order.getPaymentConditionTradeDate())
    self.assertEquals(DateTime(2001, 01, 01),
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
    
    self.assertEquals(self.vendor, self.order.getSourceSectionValue())
    self.assertEquals(self.vendor, self.order.getSourceValue())
    self.assertEquals(self.client, self.order.getDestinationSectionValue())
    self.assertEquals(self.client, self.order.getDestinationValue())
    self.assertEquals(self.currency, self.order.getPriceCurrencyValue())
    self.assertEquals('custom', self.order.getPaymentConditionTradeDate())
    self.assertEquals(DateTime(2001, 01, 01),
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
    self.assertEquals(new_vendor, self.order.getSourceSectionValue())
    self.assertEquals(self.vendor, self.order.getSourceValue())
    self.assertEquals(self.client, self.order.getDestinationSectionValue())
    self.assertEquals(self.client, self.order.getDestinationValue())
    self.assertEquals(self.currency, self.order.getPriceCurrencyValue())
    self.assertEquals('custom', self.order.getPaymentConditionTradeDate())
    self.assertEquals(DateTime(2002, 02, 02),
                      self.order.getPaymentConditionPaymentDate())


  def test_tax_model_line_consistency(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    self.assertEquals([], tax_model_line.checkConsistency())
    self.assertEquals([], self.trade_condition.checkConsistency())
  
  def test_discount_model_line_consistency(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    discount_model_line = self.trade_condition.newContent(
                  portal_type='Discount Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.discount)
    self.assertEquals([], discount_model_line.checkConsistency())
    self.assertEquals([], self.trade_condition.checkConsistency())

  def test_view_tax_model_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    # TODO: fail if a field has an error
    tax_model_line.view()
    self.trade_condition.TradeCondition_viewTax()

  def test_view_discount_model_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    discount_model_line = self.trade_condition.newContent(
                  portal_type='Discount Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.discount)
    # TODO: fail if a field has an error
    discount_model_line.view()
    self.trade_condition.TradeCondition_viewDiscount()

  def test_tax_line_consistency(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    tax_line = self.order.newContent(
                        portal_type='Tax Line',
                        resource_value=self.tax,
                        base_application_value=base_1,
                        quantity=0,
                        efficiency=5.5)
    self.assertEquals([], tax_line.checkConsistency())

  def test_view_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    tax_line = self.order.newContent(
                        portal_type='Tax Line',
                        resource_value=self.tax,
                        base_application_value=base_1,
                        quantity=0,
                        efficiency=5.5)
    # TODO: fail if a field has an error
    tax_line.view()
    self.order.Delivery_viewTax()

  def test_discount_line_consistency(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    discount_line = self.order.newContent(
                        portal_type='Discount Line',
                        resource_value=self.discount,
                        base_application_value=base_1,
                        quantity=0,
                        efficiency=5.5)
    self.assertEquals([], discount_line.checkConsistency())

  def test_view_discount_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    discount_line = self.order.newContent(
                        portal_type='Discount Line',
                        resource_value=self.discount,
                        base_application_value=base_1,
                        quantity=0,
                        efficiency=5.5)
    # TODO: fail if a field has an error
    discount_line.view()
    self.order.Delivery_viewDiscount()


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

    self.assertEquals(self.vendor, supply_line.getSourceValue())
    self.assertEquals(self.vendor, supply_line.getSourceSectionValue())
    self.assertEquals(self.client, supply_line.getDestinationValue())
    self.assertEquals(self.client, supply_line.getDestinationSectionValue())
    self.assertEquals(self.currency, supply_line.getPriceCurrencyValue())

  def test_movement_price_assignment(self):
    # supply line from the trade condition apply to the movements in order
    # where this trade condition is used
    supply_line = self.trade_condition.newContent(
                                    portal_type=self.supply_line_type,
                                    resource_value=self.resource,
                                    base_price=123)

    self.order.setSpecialiseValue(self.trade_condition)
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    self.assertEquals(123, line.getPrice())

  def test_supply_line_priority(self):
    # supply lines from related trade condition should have priority over
    # supply lines from supply modules
    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          source_section_value=self.vendor,
                                          destination_section_value=self.client)
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
    self.assertEquals(2, line.getPrice())

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
    supply_line = supply.newContent(
                                    portal_type=self.supply_line_type,
                                    base_price=1)

    other_supply = self.portal.getDefaultModule(self.supply_type
                             ).newContent(portal_type=self.supply_type,
                                          resource_value=self.resource,
                                          destination_section_value=self.client,
                                          source_section_value=self.vendor)
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
    self.assertEquals(2, line.getPrice())


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
    
    self.assertEquals(other_trade_condition,
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
    self.assertEquals(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

  def test_getEffectiveModel_without_dates(self):
    # a trade condition without effective / expiration date is effective
    self.trade_condition.setReference(self.id())
    self.trade_condition.setEffectiveDate(None)
    self.trade_condition.setExpirationDate(None)
    self.tic()
    self.assertEquals(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

    self.trade_condition.setEffectiveDate(None)
    self.trade_condition.setExpirationDate('2009/12/31')
    self.tic()
    self.assertEquals(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

    self.trade_condition.setEffectiveDate('2009/01/01')
    self.trade_condition.setExpirationDate(None)
    self.tic()
    self.assertEquals(self.trade_condition,
        self.trade_condition.getEffectiveModel(
                    start_date=DateTime('2009/06/01'),
                    stop_date=DateTime('2009/06/01')))

    
  def test_getEffectiveModel_return_self_when_no_reference(self):
    # when no reference defined, getEffectiveModel returns the trade condition.
    self.trade_condition.setReference(None)
    self.assertEquals(self.trade_condition,
        self.trade_condition.getEffectiveModel())
    self.assertEquals(self.trade_condition,
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

