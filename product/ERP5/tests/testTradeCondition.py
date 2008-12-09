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

import transaction
from DateTime import DateTime

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase

try:
  from transaction import get as get_transaction
except ImportError:
  pass

class TradeConditionTestCase(ERP5TypeTestCase):
  """Tests for Trade Conditions and Tax
  """
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting', 'erp5_invoicing')

  def setUp(self):
    ERP5TypeTestCase.setUp(self)
    self.validateRules()
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

  def tearDown(self):
    get_transaction().abort()
    for module in (self.portal.tax_module,
                   self.portal.organisation_module,
                   self.portal.currency_module,
                   self.portal.product_module,
                   self.portal.accounting_module,
                   self.portal.account_module,
                   self.portal.portal_simulation,
                   self.trade_condition_module,
                   self.order_module,
                   self.portal.portal_categories.base_amount,):
      module.manage_delObjects(list(module.objectIds()))
    if 'test_invoice_transaction_rule' in self.portal.portal_rules.objectIds():
      self.portal.portal_rules.manage_delObjects('test_invoice_transaction_rule')
    get_transaction().commit()
    self.tic()
    ERP5TypeTestCase.tearDown(self)


class AccountingBuildTestCase(TradeConditionTestCase):
  """Same as TradeConditionTestCase, but with a rule to generate
  accounting.
  """
  def setUp(self):
    TradeConditionTestCase.setUp(self)
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
    get_transaction().commit()
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
    get_transaction().commit()
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


class TestTaxLineCalculation(TradeConditionTestCase):
  """Test calculating Tax Lines.
  """
  def test_apply_trade_condition_twice_and_tax_lines(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
    
    # if we apply twice, we don't have the tax lines twice
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))

  def test_apply_trade_condition_after_line_creation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    transaction.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

  def test_simple_tax_model_line_calculation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    transaction.commit()
    # at the end of transaction, tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
  def test_tax_model_line_calculation_with_two_lines(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line_1 = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=3,
                          price=10,)
    order_line_2 = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=7,
                          price=10,)
    
    transaction.commit()
    # at the end of transaction, tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    order_line_1_tax_line_list = \
      order_line_1.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(1, len(order_line_1_tax_line_list))
    tax_line = order_line_1_tax_line_list[0]
    self.assertEquals(30, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(6, tax_line.getTotalPrice())

    order_line_2_tax_line_list = \
      order_line_2.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(1, len(order_line_2_tax_line_list))
    tax_line = order_line_2_tax_line_list[0]
    self.assertEquals(70, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(14, tax_line.getTotalPrice())

  def test_tax_on_tax(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    base_2 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 2')
    tax2 = self.portal.tax_module.newContent(
                          portal_type='Tax',
                          title='Tax 2')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  base_contribution_value=base_2,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_2,
                  float_index=2,
                  efficiency=0.5,
                  resource_value=tax2)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    transaction.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(2, len(tax_line_list))
    tax_line1 = [tl for tl in tax_line_list if
                   tl.getResourceValue() == self.tax][0]
    self.assertEquals(0, tax_line1.getQuantity())
    self.assertEquals(0.2, tax_line1.getPrice())
    self.assertEquals(1, tax_line1.getFloatIndex())
    self.assertEquals([base_1], tax_line1.getBaseApplicationValueList())
    self.assertEquals([base_2], tax_line1.getBaseContributionValueList())

    tax_line2 = [tl for tl in tax_line_list if
                   tl.getResourceValue() == tax2][0]
    self.assertEquals(0, tax_line2.getQuantity())
    self.assertEquals(0.5, tax_line2.getPrice())
    self.assertEquals(2, tax_line2.getFloatIndex())
    self.assertEquals([base_2], tax_line2.getBaseApplicationValueList())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=3,
                          price=10,)
    transaction.commit()
    self.assertEquals(30, tax_line1.getQuantity())
    self.assertEquals((30*0.2), tax_line2.getQuantity())
    
    order_line.setQuantity(5)
    transaction.commit()
    self.assertEquals(50, tax_line1.getQuantity())
    self.assertEquals((50*0.2), tax_line2.getQuantity())
    
    tax_movement_list = order_line.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(2, len(tax_movement_list))
    tax_1_movement = [m for m in tax_movement_list if m.getPrice() == 0.2][0]
    self.assertEquals(tax_1_movement.getQuantity(), 50)
    tax_2_movement = [m for m in tax_movement_list if m.getPrice() == 0.5][0]
    self.assertEquals(tax_2_movement.getQuantity(), 50*0.2)


  def test_update_order_line_quantity_update_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    transaction.commit()
    # tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    # change the quantity on order_line,
    order_line.setQuantity(20)
    transaction.commit()
    # the tax line is updated (by an interraction workflow at the end of
    # transaction)
    self.assertEquals(200, tax_line.getQuantity())
    self.assertEquals(40, tax_line.getTotalPrice())

  def test_delete_order_line_quantity_update_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)

    transaction.commit()
    # tax lines are updated
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(20, tax_line.getTotalPrice())
    
    # delete the order line
    self.order.manage_delObjects([order_line.getId()])
    # the tax line is updated
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(0, tax_line.getTotalPrice())

  def test_order_cell_and_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    # make a resource with size variation
    self.portal.portal_categories.size.newContent(id='small', title='Small')
    self.portal.portal_categories.size.newContent(id='big', title='Big')
    self.resource.setVariationBaseCategoryList(('size',))
    self.resource.setVariationCategoryList(('size/big', 'size/small'))

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,)
    order_line.setVariationCategoryList(('size/big', 'size/small'))
    order_line.updateCellRange(base_id='movement')
    cell_red = order_line.newCell('size/big',
                                  portal_type=self.order_cell_type,
                                  base_id='movement')
    cell_red.setMappedValuePropertyList(['quantity', 'price'])
    cell_red.setPrice(5)
    cell_red.setQuantity(10)
    cell_blue = order_line.newCell('size/small',
                             portal_type=self.order_cell_type,
                             base_id='movement')
    cell_blue.setMappedValuePropertyList(['quantity', 'price'])
    cell_blue.setPrice(2)
    cell_blue.setQuantity(25)
    self.assertEquals(100, order_line.getTotalPrice(fast=0))
    
    transaction.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
    
    self.assertEquals(100, self.order.getTotalPrice(fast=0))
    self.assertEquals(120, self.order.getTotalNetPrice(fast=0))


  def test_hierarchical_order_line_and_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)

    # this creates a tax line, with quantity 0, and it will be updated when
    # needed
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = self.order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,)
    suborder_line1 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=4,
                          price=5)
    suborder_line2 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=2,
                          price=40)

    transaction.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
  
  def test_base_contribution_pseudo_acquisition(self):
    base_1 = self.base_amount.newContent(portal_type='Category',
                                         title='Base 1')
    self.resource.setBaseContributionValueList((base_1,))
    line = self.order.newContent(portal_type=self.order_line_type)
    self.assertEquals([], line.getBaseContributionValueList())
    line.setResourceValue(self.resource)
    self.assertEquals([base_1], line.getBaseContributionValueList())
    line.setBaseContributionValueList([])
    self.assertEquals([], line.getBaseContributionValueList())

  def test_multiple_order_line_multiple_tax_line(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    base_2 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 2')
    self.resource.setBaseContributionValueList((base_1, base_2))
    tax_model_line_1 = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.1,
                  resource_value=self.tax)
    tax_model_line_2 = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_2,
                  float_index=2,
                  efficiency=0.2,
                  resource_value=self.tax)
    tax_model_line_1_2 = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value_list=(base_1, base_2),
                  float_index=3,
                  efficiency=0.3,
                  resource_value=self.tax)
    
    self.order.Order_applyTradeCondition(self.trade_condition, force=1)
    line_1 = self.order.newContent(
                  portal_type=self.order_line_type,
                  quantity=1, price=1,
                  resource_value=self.resource,
                  base_contribution_value_list=(base_1,))
    # -> tax_model_line_1 and tax_model_line_1_2 are applicable
    line_2 = self.order.newContent(
                  portal_type=self.order_line_type,
                  quantity=2, price=2,
                  resource_value=self.resource,
                  base_contribution_value_list=(base_2,))
    # -> tax_model_line_2 and tax_model_line_1_2 are applicable
    line_3 = self.order.newContent(
                  portal_type=self.order_line_type,
                  quantity=3, price=3,
                  resource_value=self.resource,
                  base_contribution_value_list=(base_1, base_2))
    # -> tax_model_line_1, tax_model_line_2 and tax_model_line_1_2 are applicable
    #  (but they are not applied twice)

    transaction.commit()
    tax_line_list = self.order.contentValues(portal_type='Tax Line')
    self.assertEquals(3, len(tax_line_list))
    tax_line_1 = [x for x in tax_line_list if x.getPrice() == 0.1][0]
    tax_line_2 = [x for x in tax_line_list if x.getPrice() == 0.2][0]
    tax_line_3 = [x for x in tax_line_list if x.getPrice() == 0.3][0]

    self.assertEquals(sum([line_1.getTotalPrice(),
                           line_3.getTotalPrice()]), tax_line_1.getQuantity())
    self.assertEquals(sum([line_2.getTotalPrice(),
                           line_3.getTotalPrice()]), tax_line_2.getQuantity())
    self.assertEquals(sum([line_1.getTotalPrice(),
                           line_2.getTotalPrice(),
                           line_3.getTotalPrice()]), tax_line_3.getQuantity())

    tax_movement_list = line_1.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(2, len(tax_movement_list))
    tax_1_movement = [m for m in tax_movement_list if m.getPrice() == 0.1][0]
    self.assertEquals(tax_1_movement.getQuantity(), 1)
    tax_3_movement = [m for m in tax_movement_list if m.getPrice() == 0.3][0]
    self.assertEquals(tax_3_movement.getQuantity(), 1)
    
    tax_movement_list = line_2.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(2, len(tax_movement_list))
    tax_2_movement = [m for m in tax_movement_list if m.getPrice() == 0.2][0]
    self.assertEquals(tax_2_movement.getQuantity(), 4)
    tax_3_movement = [m for m in tax_movement_list if m.getPrice() == 0.3][0]
    self.assertEquals(tax_3_movement.getQuantity(), 4)
    
    tax_movement_list = line_3.DeliveryMovement_getCorrespondingTaxLineList()
    self.assertEquals(3, len(tax_movement_list))
    tax_1_movement = [m for m in tax_movement_list if m.getPrice() == 0.1][0]
    self.assertEquals(tax_1_movement.getQuantity(), 9)
    tax_2_movement = [m for m in tax_movement_list if m.getPrice() == 0.2][0]
    self.assertEquals(tax_2_movement.getQuantity(), 9)
    tax_3_movement = [m for m in tax_movement_list if m.getPrice() == 0.3][0]
    self.assertEquals(tax_3_movement.getQuantity(), 9)
    
  def test_temp_order(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)

    order = self.portal.getDefaultModule(self.order_type).newContent(
                          portal_type=self.order_type,
                          temp_object=1)
    order.Order_applyTradeCondition(self.trade_condition, force=1)

    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=40)
    transaction.commit()

    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(400, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
  
  def test_temp_order_hierarchical(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)

    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)

    order = self.portal.getDefaultModule(self.order_type).newContent(
                          portal_type=self.order_type,
                          temp_object=1)
    order.Order_applyTradeCondition(self.trade_condition, force=1)

    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(0, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())

    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,)
    suborder_line1 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=4,
                          price=5)
    suborder_line2 = order_line.newContent(
                          portal_type=self.order_line_type,
                          quantity=2,
                          price=40)

    transaction.commit()
    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(0.2, tax_line.getPrice())
  

class TestTaxLineOrderSimulation(AccountingBuildTestCase):
  """Test Simulation of Tax Lines on Orders
  """
  def test_tax_line_simulation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_applied_rule_list = order.getCausalityRelatedValueList(
                                      portal_type='Applied Rule')
    self.assertEquals(1, len(related_applied_rule_list))
    root_applied_rule = related_applied_rule_list[0]
    simulation_movement_list = root_applied_rule.contentValues(
                                   portal_type='Simulation Movement')
    self.assertEquals(1, len(simulation_movement_list))
    level2_applied_rule_list = simulation_movement_list[0].contentValues()
    self.assertEquals(2, len(level2_applied_rule_list))
    # first test the invoice movement, they should have base_contribution set
    # correctly
    invoice_rule_list = [ar for ar in level2_applied_rule_list if
             ar.getSpecialiseValue().getPortalType() == 'Invoicing Rule']
    self.assertEquals(1, len(invoice_rule_list))
    invoice_simulation_movement_list = invoice_rule_list[0].contentValues()
    self.assertEquals(1, len(invoice_simulation_movement_list))
    invoice_simulation_movement = invoice_simulation_movement_list[0]
    self.assertEquals(self.resource,
        invoice_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
        invoice_simulation_movement.getBaseContributionValueList())

    # now test the tax movement
    applied_tax_rule_list = [ar for ar in level2_applied_rule_list if
             ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]

    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(100, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())
    
    # reexpand and check nothing changed
    root_applied_rule.expand()
    applied_tax_rule_list = [ar for ar in level2_applied_rule_list if
             ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]

    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(100, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())

  def test_2_tax_lines_simulation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line1 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order_line2 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=7,
                          price=10,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_applied_rule_list = order.getCausalityRelatedValueList(
                                      portal_type='Applied Rule')
    self.assertEquals(1, len(related_applied_rule_list))
    root_applied_rule = related_applied_rule_list[0]
    simulation_movement_list = root_applied_rule.contentValues(
                                   portal_type='Simulation Movement')
    self.assertEquals(2, len(simulation_movement_list))
    # line 1
    line1_simulation_movement_list = [sm for sm in simulation_movement_list
          if sm.getOrderValue() == order_line1]
    self.assertEquals(1, len(line1_simulation_movement_list))
    simulation_movement = line1_simulation_movement_list[0]
    self.assertEquals(2.0, simulation_movement.getQuantity())
    applied_tax_rule_list = [ar for ar in simulation_movement.objectValues()
        if ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]
    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(30, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())
    
    # line 2
    line2_simulation_movement_list = [sm for sm in simulation_movement_list
          if sm.getOrderValue() == order_line2]
    self.assertEquals(1, len(line2_simulation_movement_list))
    simulation_movement = line2_simulation_movement_list[0]
    self.assertEquals(7., simulation_movement.getQuantity())
    applied_tax_rule_list = [ar for ar in simulation_movement.objectValues()
        if ar.getSpecialiseValue().getPortalType() == 'Tax Rule']
    self.assertEquals(1, len(applied_tax_rule_list))
    tax_simulation_movement_list = applied_tax_rule_list[0].contentValues()
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]
    self.assertEquals(self.tax, tax_simulation_movement.getResourceValue())
    self.assertEquals([base_1],
                      tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(70, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())


  def test_tax_line_build(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    get_transaction().commit()
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    invoice_line_list = related_invoice.contentValues(
                  portal_type='Invoice Line')
    tax_line_list = related_invoice.contentValues(
                  portal_type='Tax Line')

    self.assertEquals(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    self.assertEquals(2, invoice_line.getQuantity())
    self.assertEquals(15, invoice_line.getPrice())
    self.assertEquals(self.resource, invoice_line.getResourceValue())
    self.assertEquals([base_1], invoice_line.getBaseContributionValueList())

    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(30, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals([base_1], tax_line.getBaseApplicationValueList())
    self.assertEquals([], tax_line.getBaseContributionValueList())

    self.assertEquals('solved', related_invoice.getCausalityState())

    # Of course, this invoice does not generate simulation again
    self.assertEquals([], related_invoice.getCausalityRelatedValueList(
                                portal_type='Applied Rule'))
    
  def test_tax_line_build_accounting(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    get_transaction().commit()
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    self.assertEquals('confirmed', related_invoice.getSimulationState())
    self.assertEquals('solved', related_invoice.getCausalityState())
    accounting_line_list = related_invoice.getMovementList(
                    portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertEquals(0, len(accounting_line_list))

    related_invoice.start()
    get_transaction().commit()
    self.tic()
    self.assertEquals('started', related_invoice.getSimulationState())
    self.assertEquals('solved', related_invoice.getCausalityState())

    accounting_line_list = related_invoice.getMovementList(
                    portal_type=self.portal.getPortalAccountingMovementTypeList())
    self.assertEquals(3, len(accounting_line_list))
    receivable_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.receivable_account][0]
    self.assertEquals(self.payable_account,
                      receivable_line.getDestinationValue())
    self.assertEquals(36, receivable_line.getSourceDebit())
    
    tax_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.collected_tax_account][0]
    self.assertEquals(self.refundable_tax_account,
                      tax_line.getDestinationValue())
    self.assertEquals(6, tax_line.getSourceCredit())

    income_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.income_account][0]
    self.assertEquals(self.expense_account,
                      income_line.getDestinationValue())
    self.assertEquals(30, income_line.getSourceCredit())

    # Of course, this invoice does not generate simulation again
    self.assertEquals([], related_invoice.getCausalityRelatedValueList(
                                portal_type='Applied Rule'))
    
    # and there's no other invoices
    self.assertEquals(1, len(self.portal.accounting_module.contentValues()))


  def test_tax_line_merged_build(self):
    # an order with 2 lines and 1 tax line will later be built in an invoice
    # with 2 lines and 1 tax line
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    resource2 = self.portal.product_module.newContent(
                            portal_type='Product',
                            title='Resource 2',
                            base_contribution_value_list=[base_1])
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line1 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order_line2 = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=resource2,
                          quantity=7,
                          price=10,)
    # check existing tax line
    tax_line_list = order.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals(2*15 + 7*10, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())

    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    get_transaction().commit()
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    invoice_line_list = related_invoice.contentValues(
                  portal_type='Invoice Line')
    tax_line_list = related_invoice.contentValues(
                  portal_type='Tax Line')

    self.assertEquals(2, len(invoice_line_list))

    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(100, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals([base_1], tax_line.getBaseApplicationValueList())
    self.assertEquals([], tax_line.getBaseContributionValueList())

    self.assertEquals('solved', related_invoice.getCausalityState())

  def test_tax_line_updated_on_invoice_line_change(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    order = self.order
    order.Order_applyTradeCondition(self.trade_condition, force=1)
    order.setSourceSectionValue(self.vendor)
    order.setSourceValue(self.vendor)
    order.setDestinationSectionValue(self.client)
    order.setDestinationValue(self.client)
    order.setPriceCurrencyValue(self.currency)
    order.setStartDate(DateTime(2001, 1, 1))
    order_line = order.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=2,
                          price=15,)
    order.plan()
    order.confirm()
    self.assertEquals('confirmed', order.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_delivery = order.getCausalityRelatedValue(
                  portal_type=('Purchase Packing List', 'Sale Packing List'))
    self.assertNotEquals(related_delivery, None)
    related_delivery.setReady()
    related_delivery.start()
    related_delivery.stop()
    related_delivery.deliver()
    self.assertEquals('delivered', related_delivery.getSimulationState())
    get_transaction().commit()
    self.tic()
    
    related_invoice = related_delivery.getCausalityRelatedValue(
                  portal_type=('Purchase Invoice Transaction',
                               'Sale Invoice Transaction'))
    self.assertNotEquals(related_invoice, None)
    self.assertEquals('solved', related_invoice.getCausalityState())
    invoice_line_list = related_invoice.contentValues(
                  portal_type='Invoice Line')
    tax_line_list = related_invoice.contentValues(
                  portal_type='Tax Line')

    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]
    self.assertEquals(30, tax_line.getQuantity())
    self.assertEquals(0.2, tax_line.getPrice())
    self.assertEquals(self.tax, tax_line.getResourceValue())
    self.assertEquals([base_1], tax_line.getBaseApplicationValueList())
    self.assertEquals([], tax_line.getBaseContributionValueList())

    self.assertEquals(1, len(invoice_line_list))
    invoice_line = invoice_line_list[0]
    # change a total price on the invoice_line,
    invoice_line.setQuantity(3)
    get_transaction().commit()
    self.tic()
    # it will be reflected on the tax line
    self.assertEquals(45, tax_line.getQuantity())
    self.assertTrue(tax_line.isDivergent())
    # and the invoice is diverged
    self.assertEquals('diverged', related_invoice.getCausalityState())
    

class TestTaxLineInvoiceSimulation(AccountingBuildTestCase):
  """Test Simulation of Tax Lines on Invoices
  """
  def test_tax_line_simulation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    tax_model_line = self.trade_condition.newContent(
                  portal_type='Tax Model Line',
                  base_application_value=base_1,
                  float_index=1,
                  efficiency=0.2,
                  resource_value=self.tax)
    
    invoice = self.order
    invoice.Order_applyTradeCondition(self.trade_condition, force=1)
    invoice.setSourceSectionValue(self.vendor)
    invoice.setSourceValue(self.vendor)
    invoice.setDestinationSectionValue(self.client)
    invoice.setDestinationValue(self.client)
    invoice.setStartDate(DateTime(2001, 1, 1))
    invoice.setPriceCurrencyValue(self.currency)
    invoice_line = invoice.newContent(
                          portal_type=self.order_line_type,
                          resource_value=self.resource,
                          quantity=10,
                          price=10,)
    tax_line_list = invoice.contentValues(portal_type='Tax Line')
    self.assertEquals(1, len(tax_line_list))
    tax_line = tax_line_list[0]

    invoice.plan()
    invoice.confirm()
    invoice.start()
    self.assertEquals('started', invoice.getSimulationState())
    get_transaction().commit()
    self.tic()
    related_applied_rule_list = invoice.getCausalityRelatedValueList(
                                      portal_type='Applied Rule')
    self.assertEquals(1, len(related_applied_rule_list))
    root_applied_rule = related_applied_rule_list[0]
    simulation_movement_list = root_applied_rule.contentValues(
                                   portal_type='Simulation Movement')
    self.assertEquals(2, len(simulation_movement_list))
    tax_simulation_movement_list = [m for m in simulation_movement_list
                                    if m.getOrderValue() == tax_line]
    self.assertEquals(1, len(tax_simulation_movement_list))
    tax_simulation_movement = tax_simulation_movement_list[0]
    self.assertEquals([base_1],
        tax_simulation_movement.getBaseApplicationValueList())
    self.assertEquals(100, tax_simulation_movement.getQuantity())
    self.assertEquals(0.2, tax_simulation_movement.getPrice())
    self.assertEquals(self.currency,
                      tax_simulation_movement.getPriceCurrencyValue())

    invoice_simulation_movement_list = [m for m in simulation_movement_list
                                    if m.getOrderValue() == invoice_line]
    self.assertEquals(1, len(invoice_simulation_movement_list))
    invoice_simulation_movement = invoice_simulation_movement_list[0]
    self.assertEquals([base_1],
        invoice_simulation_movement.getBaseContributionValueList())
    self.assertEquals(10, invoice_simulation_movement.getQuantity())
    self.assertEquals(10, invoice_simulation_movement.getPrice())
    self.assertEquals(self.currency,
                      invoice_simulation_movement.getPriceCurrencyValue())
    self.assertEquals(self.resource,
                      invoice_simulation_movement.getResourceValue())
    invoice.start()
    self.assertEquals('started', invoice.getSimulationState())
    get_transaction().commit()
    self.tic()
    accounting_line_list = invoice.getMovementList(
                            portal_type=('Sale Invoice Transaction Line',
                                         'Purchase Invoice Transaction Line'))
    self.assertEquals(3, len(accounting_line_list))
    receivable_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.receivable_account][0]
    self.assertEquals(self.payable_account,
                      receivable_line.getDestinationValue())
    self.assertEquals(120, receivable_line.getSourceDebit())
    
    tax_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.collected_tax_account][0]
    self.assertEquals(self.refundable_tax_account,
                      tax_line.getDestinationValue())
    self.assertEquals(20, tax_line.getSourceCredit())

    income_line = [l for l in accounting_line_list if
                        l.getSourceValue() == self.income_account][0]
    self.assertEquals(self.expense_account,
                      income_line.getDestinationValue())
    self.assertEquals(100, income_line.getSourceCredit())

    self.assertEquals('solved', invoice.getCausalityState())


class DiscountCalculation:
  """Test Discount Calculations
  """
  def test_simple_discount_model_line_calculation(self):
    base_1 = self.base_amount.newContent(
                          portal_type='Category',
                          title='Base 1')
    self.resource.setBaseContributionValue(base_1)
    discount_model_line =self.trade_condition.newContent(
                    portal_type='Discount Model Line',
                    base_application_value=base_1,
                    float_index=1,
                    efficiency=0.2,
                    resource_value=self.discount)
  

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
    get_transaction().commit()
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
    get_transaction().commit()
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
    get_transaction().commit()
    self.tic()

    line = self.order.newContent(portal_type=self.order_line_type,
                                 resource_value=self.resource,
                                 quantity=1)
    # using the supply line with section defined
    self.assertEquals(2, line.getPrice())


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

class TestTaxLineCalculationSaleOrder(
    TestTaxLineCalculation, TestWithSaleOrder):
  pass
class TestTaxLineCalculationPurchaseOrder(
    TestTaxLineCalculation, TestWithPurchaseOrder):
  pass
class TestTaxLineCalculationSaleInvoice(
    TestTaxLineCalculation, TestWithSaleInvoice):
  def not_available(self):
    pass
  test_hierarchical_order_line_and_tax_line = not_available
  test_temp_order_hierarchical = not_available
class TestTaxLineCalculationPurchaseInvoice(
    TestTaxLineCalculation, TestWithPurchaseInvoice):
  def not_available(self):
    pass
  test_hierarchical_order_line_and_tax_line = not_available
  test_temp_order_hierarchical = not_available

class TestTaxLineOrderSimulationSaleOrder(
      TestTaxLineOrderSimulation, TestWithSaleOrder):
  pass
class TestTaxLineOrderSimulationPurchaseOrder(
      TestTaxLineOrderSimulation, TestWithPurchaseOrder):
  pass

class TestTaxLineInvoiceSimulationPurchaseInvoice(
      TestTaxLineInvoiceSimulation, TestWithPurchaseInvoice):
  pass
class TestTaxLineInvoiceSimulationSaleInvoice(
      TestTaxLineInvoiceSimulation, TestWithSaleInvoice):
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



def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestApplyTradeConditionSaleOrder))
  suite.addTest(unittest.makeSuite(TestApplyTradeConditionPurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationSaleOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationPurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationSaleInvoice))
  suite.addTest(unittest.makeSuite(TestTaxLineCalculationPurchaseInvoice))
  suite.addTest(unittest.makeSuite(TestTaxLineOrderSimulationSaleOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineOrderSimulationPurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTaxLineInvoiceSimulationPurchaseInvoice))
  suite.addTest(unittest.makeSuite(TestTaxLineInvoiceSimulationSaleInvoice))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLineSaleOrder))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLinePurchaseOrder))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLineSaleInvoice))
  suite.addTest(unittest.makeSuite(TestTradeConditionSupplyLinePurchaseInvoice))
  return suite

