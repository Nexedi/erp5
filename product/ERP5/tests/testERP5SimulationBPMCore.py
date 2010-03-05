# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################
import transaction

from Products.ERP5.tests.testBPMCore import TestBPMMixin, test_suite

if True:
  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
      'erp5_invoicing', 'erp5_simplified_invoicing', 'erp5_simulation')

  TestBPMMixin.getBusinessTemplateList = getBusinessTemplateList

  def createInvoiceTransactionRule(self):
    self.receivable_account = self.createAndValidateAccount('receivable',
        'asset/receivable')
    self.payable_account = self.createAndValidateAccount('payable',
        'liability/payable')
    self.income_account = self.createAndValidateAccount('income', 'income')
    self.expense_account = self.createAndValidateAccount('expense', 'expense')
    self.collected_tax_account = self.createAndValidateAccount(
        'collected_tax', 'liability/payable/collected_vat')
    self.refundable_tax_account = self.createAndValidateAccount(
        'refundable_tax',
        'asset/receivable/refundable_vat')

    itr = self.portal.portal_rules.newContent(
                        portal_type='Invoice Transaction Simulation Rule',
                        reference='default_invoice_transaction_rule',
                        id='test_invoice_transaction_simulation_rule',
                        title='Transaction Simulation Rule',
                        test_method_id=
                        'SimulationMovement_testInvoiceTransactionSimulationRule',
                        version=100)
    # matching provider for source and destination
    for category in ('resource', 'source', 'destination',
                     'destination_total_asset_price',
                     'source_total_asset_price'):
      itr.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    # non-matching/non-divergence provider quantity divergence tester
    # (i.e. only used for expand)
    itr.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=False,
      matching_provider=False)
    # divergence provider for date
    for property_id in ('start_date', 'stop_date'):
      itr.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    for category in ('source_administration', 'source_decision', 'source_function', 'source_payment', 'source_project', 'source_section', 'destination_administration', 'destination_decision', 'destination_function', 'destination_payment', 'destination_project', 'destination_section'):
      itr.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    itr.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    predicate = itr.newContent(portal_type='Predicate',)
    predicate.edit(
            string_index='use',
            title='tax',
            int_index=1,
            membership_criterion_base_category='resource_use',
            membership_criterion_category='resource_use/use/tax')
    predicate = itr.newContent(portal_type='Predicate',)
    predicate.edit(
            string_index='use',
            title='discount',
            int_index=2,
            membership_criterion_base_category='resource_use',
            membership_criterion_category='resource_use/use/discount')
    predicate = itr.newContent(portal_type='Predicate',)
    predicate.edit(
            string_index='use',
            title='normal',
            int_index=3,
            membership_criterion_base_category='resource_use',
            membership_criterion_category='resource_use/use/normal')
    transaction.commit()
    self.tic()
    accounting_rule_cell_list = itr.contentValues(
                            portal_type='Accounting Rule Cell')
    self.assertEquals(3, len(accounting_rule_cell_list))
    tax_rule_cell = itr._getOb("movement_0")
    self.assertEquals(tax_rule_cell.getTitle(), 'tax')
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

    discount_rule_cell = itr._getOb("movement_1")
    self.assertEquals(discount_rule_cell.getTitle(), 'discount')
    discount_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.receivable_account,
                         destination_value=self.payable_account,
                         quantity=-1)
    discount_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.income_account,
                         destination_value=self.expense_account,
                         quantity=1)

    normal_rule_cell = itr._getOb("movement_2")
    self.assertEquals(normal_rule_cell.getTitle(), 'normal')
    normal_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.receivable_account,
                         destination_value=self.payable_account,
                         quantity=-1)
    normal_rule_cell.newContent(
                         portal_type='Accounting Transaction Line',
                         source_value=self.income_account,
                         destination_value=self.expense_account,
                         quantity=1)

    itr.validate()

  TestBPMMixin.createInvoiceTransactionRule = createInvoiceTransactionRule
