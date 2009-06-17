# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#          Yusuke Muraoka <yusuke@nexedi.com>
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
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime

from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.utils import reindex

# XXX TODO:
#  * move test.* methods to other classes, group by testing area
#  * subclass TestBPMMixin from TestInvoiceMixin and refactor methods and
#    style

class TestBPMMixin(ERP5TypeTestCase):
  """Skeletons for tests for ERP5 BPM"""

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_trade', 'erp5_accounting',
      'erp5_invoicing', 'erp5_mrp', 'erp5_bpm')

  default_discount_ratio = -0.05 # -5%
  default_tax_ratio = 0.196 # 19,6%

  new_discount_ratio = -0.04 # -4%
  new_tax_ratio = 0.22 # 22%

  node_portal_type = 'Organisation'
  order_date = DateTime()
  default_business_process = \
      'business_process_module/erp5_default_business_process'

  business_process_portal_type = 'Business Process'
  business_path_portal_type = 'Business Path'
  business_state_portal_type = 'Business State'

  modified_order_line_price_ratio = 2.0
  modified_invoice_line_quantity_ratio = modified_order_line_quantity_ratio \
      = 2.5

  modified_packing_list_line_quantity_ratio = 0.5

  base_unit_quantity = 0.01

  normal_resource_use_category_list = ['normal']
  invoicing_resource_use_category_list = ['discount', 'tax']

  def setUpOnce(self):
    self.portal = self.getPortalObject()
    self.validateRules()

  def createCategoriesInCategory(self, category, category_id_list):
    for category_id in category_id_list:
      if getattr(category,category_id,None) is None:
        category.newContent(portal_type='Category', id = category_id,
            title = category_id)

  @reindex
  def createCategories(self):
    category_tool = getToolByName(self.portal, 'portal_categories')
    self.createCategoriesInCategory(category_tool.base_amount, ['discount',
      'tax', 'total_tax', 'total_discount', 'total'])
    self.createCategoriesInCategory(category_tool.use,
        self.normal_resource_use_category_list + \
            self.invoicing_resource_use_category_list)
    self.createCategoriesInCategory(category_tool.trade_phase, ['default',])
    self.createCategoriesInCategory(category_tool.trade_phase.default,
        ['accounting', 'delivery', 'invoicing', 'discount', 'tax', 'payment'])

  @reindex
  def createBusinessProcess(self):
    module = self.portal.getDefaultModule(
        portal_type=self.business_process_portal_type)
    return module.newContent(portal_type=self.business_process_portal_type)

  def stepCreateBusinessProcess(self, sequence=None, **kw):
    sequence.edit(business_process=self.createBusinessProcess())

  @reindex
  def createBusinessPath(self, business_process=None):
    if business_process is None:
      business_process = self.portal.business_process_module.newContent(
        portal_type=self.business_process_portal_type)
    business_path = business_process.newContent(
      portal_type=self.business_path_portal_type)
    return business_path

  def stepCreateBusinessPath(self, sequence=None, **kw):
    business_process = sequence.get('business_process')
    sequence.edit(business_path=self.createBusinessPath(business_process))

  def stepModifyBusinessPathTaxing(self, sequence=None, **kw):
    predecessor = sequence.get('business_state_invoiced')
    successor = sequence.get('business_state_taxed')
    business_path = sequence.get('business_path')
    self.assertNotEqual(None, predecessor)
    self.assertNotEqual(None, successor)

    business_path.edit(
      predecessor_value = predecessor,
      successor_value = successor,
      trade_phase = 'default/tax'
    )
    sequence.edit(business_path=None, business_path_taxing=business_path)

  def _solveDivergence(self, obj, property, decision, group='line'):
    kw = {'%s_group_listbox' % group:{}}
    for divergence in obj.getDivergenceList():
      if divergence.getProperty('tested_property') != property:
        continue
      sm_url = divergence.getProperty('simulation_movement').getRelativeUrl()
      kw['line_group_listbox']['%s&%s' % (sm_url, property)] = {
        'choice':decision}
    self.portal.portal_workflow.doActionFor(
      obj,
      'solve_divergence_action',
      **kw)

  def stepAcceptDecisionQuantityInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'quantity', 'accept')

  def stepAdoptPrevisionQuantityInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'quantity', 'adopt')

  def stepModifyBusinessPathDiscounting(self, sequence=None, **kw):
    predecessor = sequence.get('business_state_invoiced')
    successor = sequence.get('business_state_taxed')
    business_path = sequence.get('business_path')
    self.assertNotEqual(None, predecessor)
    self.assertNotEqual(None, successor)

    business_path.edit(
      predecessor_value = predecessor,
      successor_value = successor,
      trade_phase = 'default/discount'
    )
    sequence.edit(business_path=None, business_path_discounting=business_path)

  @reindex
  def createBusinessState(self, business_process=None):
    if business_process is None:
      business_process = self.portal.business_process_module.newContent(
                           portal_type=self.business_process_portal_type)
    business_path = business_process.newContent(
        portal_type=self.business_state_portal_type)
    return business_path

  def stepCreateBusinessState(self, sequence=None, **kw):
    business_process = sequence.get('business_process')
    sequence.edit(business_state=self.createBusinessState(business_process))

  def stepModifyBusinessStateTaxed(self, sequence=None, **kw):
    business_state = sequence.get('business_state')
    business_state.edit(reference='taxed')
    sequence.edit( business_state=None, business_state_taxed=business_state)

  def stepModifyBusinessStateInvoiced(self, sequence=None,
                sequence_string=None):
    business_state = sequence.get('business_state')
    business_state.edit(reference='invoiced')
    sequence.edit(business_state=None, business_state_invoiced=business_state)

  def createMovement(self):
    # returns a movement for testing
    applied_rule = self.portal.portal_simulation.newContent(
        portal_type='Applied Rule')
    return applied_rule.newContent(portal_type='Simulation Movement')

  @reindex
  def setSystemPreference(self):
    preference_tool = getToolByName(self.portal, 'portal_preferences')
    system_preference_list = preference_tool.contentValues(
        portal_type='System Preference')
    if len(system_preference_list) > 1:
      raise AttributeError('More than one System Preference, cannot test')
    if len(system_preference_list) == 0:
      system_preference = preference_tool.newContent(
          portal_type='System Preference')
    else:
      system_preference = system_preference_list[0]
    system_preference.edit(
      preferred_invoicing_resource_use_category_list = \
          self.invoicing_resource_use_category_list,
      preferred_normal_resource_use_category_list = \
          self.normal_resource_use_category_list,
      priority = 1,

    )

    if system_preference.getPreferenceState() == 'disabled':
      system_preference.enable()

  @reindex
  def createAndValidateAccount(self, account_id, account_type):
    account_module = self.portal.account_module
    account = account_module.newContent(portal_type='Account',
          title=account_id,
          account_type=account_type)
    self.assertNotEqual(None, account.getAccountTypeValue())
    account.validate()
    return account

  def createInvoiceTransationRule(self):
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
                        portal_type='Invoice Transaction Rule',
                        reference='default_invoice_transaction_rule',
                        id='test_invoice_transaction_rule',
                        title='Transaction Rule',
                        test_method_id=
                        'SimulationMovement_testInvoiceTransactionRule',
                        version=100)
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

  @reindex
  def afterSetUp(self):
    self.createCategories()
    self.setSystemPreference()
    self.createInvoiceTransationRule()

  @reindex
  def beforeTearDown(self):
    self.portal.portal_rules.manage_delObjects(
        ids=['test_invoice_transaction_rule'])

  def stepCreateSource(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type=self.node_portal_type)
    node = module.newContent(portal_type=self.node_portal_type)
    sequence.edit(source = node)

  def stepCreateSourceSection(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type=self.node_portal_type)
    node = module.newContent(portal_type=self.node_portal_type)
    sequence.edit(source_section = node)

  def stepCreateDestination(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type=self.node_portal_type)
    node = module.newContent(portal_type=self.node_portal_type)
    sequence.edit(destination = node)

  def stepCreateDestinationSection(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type=self.node_portal_type)
    node = module.newContent(portal_type=self.node_portal_type)
    sequence.edit(destination_section = node)

  def createOrder(self):
    module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    return module.newContent(portal_type=self.order_portal_type,
        title=self.id())

  def stepCreateOrder(self, sequence=None, **kw):
    sequence.edit(order = self.createOrder())

  def stepSpecialiseOrderTradeCondition(self, sequence=None, **kw):
    order = sequence.get('order')
    trade_condition = sequence.get('trade_condition')

    order.edit(specialise_value = trade_condition)

  def stepSpecialiseInvoiceTradeCondition(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    trade_condition = sequence.get('trade_condition')

    invoice.edit(specialise_value = trade_condition)

  def stepPlanOrder(self, sequence=None, **kw):
    order = sequence.get('order')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(order, 'plan_action')

  def stepStartInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(invoice, 'start_action')

  def stepStopInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(invoice, 'stop_action')

  def stepDeliverInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(invoice, 'deliver_action')

  def stepStartPackingList(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(packing_list, 'start_action')

  def stepStopPackingList(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(packing_list, 'stop_action')

  def stepDeliverPackingList(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(packing_list, 'deliver_action')

  def stepCheckPackingListDiverged(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    self.assertEqual(
      'diverged',
      packing_list.getCausalityState()
    )

  def stepSplitAndDeferPackingList(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    kw = {'listbox':[
      {'listbox_key':line.getRelativeUrl(),
       'choice':'SplitAndDefer'} for line in packing_list.getMovementList() \
      if line.isDivergent()]}
    self.portal.portal_workflow.doActionFor(
      packing_list,
      'split_and_defer_action',
      start_date=packing_list.getStartDate() + 15,
      stop_date=packing_list.getStopDate() + 25,
      **kw)

  def stepDecreasePackingListLineListQuantity(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    for movement in packing_list.getMovementList():
      movement.edit(
        quantity = movement.getQuantity() * \
            self.modified_packing_list_line_quantity_ratio
      )

  def stepPackPackingList(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    if getattr(packing_list,'getContainerState', None) is None:
      return
    if packing_list.getContainerState() == 'packed':
      return

    packing_list.manage_delObjects(ids=[q.getId() for q in
      packing_list.objectValues(portal_type='Container')])
    transaction.commit()
    cntr = packing_list.newContent(portal_type='Container')
    for movement in packing_list.getMovementList(
        portal_type=self.portal.getPortalMovementTypeList()):
      cntr.newContent(
        portal_type='Container Line',
        resource = movement.getResource(),
        quantity = movement.getQuantity())
    transaction.commit()
    self.tic()
    self.assertEqual('packed', packing_list.getContainerState() )

  def stepCheckInvoiceNormalMovements(self, sequence=None, **kw):
    self.logMessage('Assuming, that it is good...')

  def stepCheckInvoiceAccountingMovements(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    currency = sequence.get('price_currency')
    currency_precision = currency.getQuantityPrecision()
    aggregated_amount_list_list = [
      (q.getResourceValue().getUse(), q)
      for q in invoice.getSpecialiseValue().getAggregatedAmountList(invoice)]
    invoice_line_tax = [q[1] for q in aggregated_amount_list_list
        if q[0] == 'tax'][0]
    invoice_line_discount = [q[1] for q in aggregated_amount_list_list
        if q[0] == 'discount'][0]

    movement_list = invoice.getMovementList(
        portal_type=invoice.getPortalAccountingMovementTypeList())
    self.assertEqual(3, len(movement_list))
    income_expense_line = [q for q in movement_list if
        q.getSourceValue().getAccountType() in ['income', 'expense']][0]
    payable_receivable_line = [q for q in movement_list if
        q.getSourceValue().getAccountType() in ['asset/receivable',
          'liability/payable']][0]
    vat_line = [q for q in movement_list if q.getSourceValue() \
        .getAccountType() in ['liability/payable/collected_vat',
          'asset/receivable/refundable_vat']][0]

    rounded_total_price = round(invoice.getTotalPrice(), currency_precision)
    rounded_tax_price = round(invoice_line_tax.getTotalPrice(),
        currency_precision)
    rounded_discount_price = round(invoice_line_discount.getTotalPrice(),
        currency_precision)

    self.assertEqual(abs(payable_receivable_line.getTotalPrice()),
        rounded_total_price + rounded_tax_price + rounded_discount_price)

    self.assertEqual(abs(vat_line.getTotalPrice()),
        rounded_tax_price)

    self.assertEquals(abs(income_expense_line.getTotalPrice()),
        rounded_total_price + rounded_discount_price)

  def stepSetTradeConditionOld(self, sequence=None, **kw):
    trade_condition = sequence.get('trade_condition')

    self.assertNotEqual(None, trade_condition)

    sequence.edit(
      trade_condition = None,
      old_trade_condition = trade_condition
    )

  def stepSetTradeConditionNew(self, sequence=None, **kw):
    trade_condition = sequence.get('trade_condition')

    self.assertNotEqual(None, trade_condition)

    sequence.edit(
      trade_condition = None,
      new_trade_condition = trade_condition
    )

  def stepGetOldTradeCondition(self, sequence=None, **kw):
    trade_condition = sequence.get('old_trade_condition')

    self.assertNotEqual(None, trade_condition)

    sequence.edit(
      trade_condition = trade_condition,
    )

  def stepGetNewTradeCondition(self, sequence=None, **kw):
    trade_condition = sequence.get('new_trade_condition')

    self.assertNotEqual(None, trade_condition)

    sequence.edit(
      trade_condition = trade_condition,
    )

  def stepAcceptDecisionInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    invoice.portal_workflow.doActionFor(invoice,'accept_decision_action')

  def stepCheckInvoiceCausalityStateSolved(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self.assertEqual('solved', invoice.getCausalityState(),
      invoice.getDivergenceList())

  def stepCheckInvoiceCausalityStateDiverged(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self.assertEqual('diverged', invoice.getCausalityState())

  def stepGetInvoice(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    invoice_list = packing_list.getCausalityRelatedValueList(
        portal_type=self.invoice_portal_type)
    self.assertEqual(1, len(invoice_list)) # XXX 1 HC
    sequence.edit(invoice = invoice_list[0])

  def stepSetNewPackingListAsPackingList(self, sequence=None, **kw):
    packing_list = sequence.get('packing_list')
    new_packing_list = sequence.get('new_packing_list')
    sequence.edit(
      packing_list = new_packing_list,
      new_packing_list = None
    )

  def stepGetNewPackingList(self, sequence=None, **kw):
    order = sequence.get('order')
    packing_list = sequence.get('packing_list')
    packing_list_list = order.getCausalityRelatedValueList(
        portal_type=self.packing_list_portal_type)
    self.assertEqual(2, len(packing_list_list)) # XXX 2 HC
    new_packing_list = [q for q in packing_list_list if q != packing_list][0]
    sequence.edit(new_packing_list = new_packing_list)

  def stepGetPackingList(self, sequence=None, **kw):
    order = sequence.get('order')
    packing_list_list = order.getCausalityRelatedValueList(
        portal_type=self.packing_list_portal_type)
    self.assertEqual(1, len(packing_list_list)) # XXX 1 HC
    sequence.edit(packing_list = packing_list_list[0])

  def stepConfirmOrder(self, sequence=None, **kw):
    order = sequence.get('order')
    workflow_tool = getToolByName(self.portal, 'portal_workflow')
    workflow_tool.doActionFor(order, 'confirm_action')

  def getTradeModelSimulationMovementList(self, order_line):
    result_list = []
    for line_simulation_movement in order_line.getOrderRelatedValueList(
        portal_type='Simulation Movement'):
      invoicing_applied_rule = [x for x in
          line_simulation_movement.objectValues()
          if x.getSpecialiseValue().getPortalType() == 'Invoicing Rule'][0]
      invoicing_movement = invoicing_applied_rule.objectValues()[0]
      trade_model_rule = [x for x in invoicing_movement.objectValues()
          if x.getSpecialiseValue().getPortalType() == 'Trade Model Rule'][0]
      result_list.append(trade_model_rule.objectValues())
    return result_list

  def stepCheckOrderTaxNoSimulation(self, sequence=None, **kw):
    order_line_taxed = sequence.get('order_line_taxed')
    for trade_model_simulation_movement_list in \
        self.getTradeModelSimulationMovementList(order_line_taxed):
      self.assertEquals(0, len(trade_model_simulation_movement_list))

  # XXX: Merge: stepCheckOrderLineDiscountedSimulation stepCheckOrderLineTaxedSimulation stepCheckOrderLineDiscountedTaxedSimulation

  def stepCheckOrderLineDiscountedTaxedSimulation(self, sequence=None, **kw):
    order_line = sequence.get('order_line_discounted_taxed')
    business_path_discounting = sequence.get('business_path_discounting')
    business_path_taxing = sequence.get('business_path_taxing')
    price_currency = sequence.get('price_currency')

    service_tax = sequence.get('service_tax')
    service_discount = sequence.get('service_discount')

    self.assertNotEqual(None, business_path_discounting)
    self.assertNotEqual(None, business_path_taxing)
    self.assertNotEqual(None, price_currency)

    for trade_model_simulation_movement_list in \
        self.getTradeModelSimulationMovementList(order_line):

      self.assertEquals(2, len(trade_model_simulation_movement_list))
      trade_model_simulation_movement_discount_complex = [q for q in \
          trade_model_simulation_movement_list \
          if q.getResourceValue() == service_discount][0]

      trade_model_simulation_movement_tax_complex = [q for q in \
          trade_model_simulation_movement_list \
          if q.getResourceValue() == service_tax][0]

      # discount complex
      self.assertEqual(
        trade_model_simulation_movement_discount_complex.getParentValue() \
            .getParentValue().getTotalPrice() * self.default_discount_ratio,
        trade_model_simulation_movement_discount_complex.getTotalPrice()
      )

      self.assertEqual(
        business_path_discounting,
        trade_model_simulation_movement_discount_complex.getCausalityValue()
      )

      self.assertEqual(
        price_currency,
        trade_model_simulation_movement_discount_complex \
            .getPriceCurrencyValue()
      )

      self.assertSameSet(
        ['base_amount/tax'],
        trade_model_simulation_movement_discount_complex \
            .getBaseContributionList()
      )

      self.assertSameSet(
        ['base_amount/discount'],
        trade_model_simulation_movement_discount_complex \
            .getBaseApplicationList()
      )

      self.checkInvoiceTransactionRule(
          trade_model_simulation_movement_discount_complex)

      # TODO:
      #  * trade_phase ???
      #  * arrow
      #  * dates

      # tax complex
      self.assertEqual(
        (trade_model_simulation_movement_tax_complex.getParentValue()\
            .getParentValue().getTotalPrice() + \
            trade_model_simulation_movement_tax_complex.getParentValue()\
            .getParentValue().getTotalPrice() * self.default_discount_ratio) \
            * self.default_tax_ratio,
        trade_model_simulation_movement_tax_complex.getTotalPrice()
      )

      self.assertEqual(
        business_path_taxing,
        trade_model_simulation_movement_tax_complex.getCausalityValue()
      )

      self.assertEqual(
        price_currency,
        trade_model_simulation_movement_tax_complex.getPriceCurrencyValue()
      )

      self.assertSameSet(
        [],
        trade_model_simulation_movement_tax_complex.getBaseContributionList()
      )

      self.assertSameSet(
        ['base_amount/tax'],
        trade_model_simulation_movement_tax_complex.getBaseApplicationList()
      )

      self.checkInvoiceTransactionRule(
        trade_model_simulation_movement_tax_complex)
      # TODO:
      #  * trade_phase ???
      #  * arrow
      #  * dates

  def stepCheckOrderLineDiscountedSimulation(self, sequence=None, **kw):
    order_line = sequence.get('order_line_discounted')
    business_path_discounting = sequence.get('business_path_discounting')
    business_path_taxing = sequence.get('business_path_taxing')
    price_currency = sequence.get('price_currency')

    service_tax = sequence.get('service_tax')
    service_discount = sequence.get('service_discount')

    self.assertNotEqual(None, business_path_discounting)
    self.assertNotEqual(None, business_path_taxing)
    self.assertNotEqual(None, price_currency)

    for trade_model_simulation_movement_list in \
        self.getTradeModelSimulationMovementList(order_line):

      self.assertEquals(2, len(trade_model_simulation_movement_list))
      trade_model_simulation_movement_discount_only = [q for q in \
          trade_model_simulation_movement_list \
          if q.getResourceValue() == service_discount][0]

      trade_model_simulation_movement_tax_only = [q for q in \
          trade_model_simulation_movement_list \
          if q.getResourceValue() == service_tax][0]

      # discount only
      self.assertEqual(
        trade_model_simulation_movement_discount_only.getParentValue()\
            .getParentValue().getTotalPrice() * self.default_discount_ratio,
        trade_model_simulation_movement_discount_only.getTotalPrice()
      )

      self.assertEqual(
        business_path_discounting,
        trade_model_simulation_movement_discount_only.getCausalityValue()
      )

      self.assertEqual(
        price_currency,
        trade_model_simulation_movement_discount_only.getPriceCurrencyValue()
      )

      self.assertSameSet(
        ['base_amount/tax'],
        trade_model_simulation_movement_discount_only \
            .getBaseContributionList()
      )

      self.assertSameSet(
        ['base_amount/discount'],
        trade_model_simulation_movement_discount_only.getBaseApplicationList()
      )

      self.checkInvoiceTransactionRule(
          trade_model_simulation_movement_discount_only)
      # TODO:
      #  * trade_phase ???
      #  * arrow
      #  * dates

      # tax only
      # below tax is applied only to discount part
      self.assertEqual(trade_model_simulation_movement_discount_only. \
          getTotalPrice() * self.default_tax_ratio,
          trade_model_simulation_movement_tax_only.getTotalPrice())

      self.assertEqual(
        business_path_taxing,
        trade_model_simulation_movement_tax_only.getCausalityValue()
      )

      self.assertEqual(
        price_currency,
        trade_model_simulation_movement_tax_only.getPriceCurrencyValue()
      )

      self.assertSameSet(
        [],
        trade_model_simulation_movement_tax_only.getBaseContributionList()
      )

      self.assertSameSet(
        ['base_amount/tax'],
        trade_model_simulation_movement_tax_only.getBaseApplicationList()
      )

      self.checkInvoiceTransactionRule(
          trade_model_simulation_movement_tax_only)

      # TODO:
      #  * trade_phase ???
      #  * arrow
      #  * dates

  def stepCheckOrderLineTaxedSimulation(self, sequence=None, **kw):
    order_line = sequence.get('order_line_taxed')
    business_path = sequence.get('business_path_taxing')
    price_currency = sequence.get('price_currency')
    self.assertNotEqual(None, business_path)
    self.assertNotEqual(None, price_currency)
    for trade_model_simulation_movement_list in \
        self.getTradeModelSimulationMovementList(order_line):
      self.assertEquals(1, len(trade_model_simulation_movement_list))
      trade_model_simulation_movement = \
          trade_model_simulation_movement_list[0]

      self.assertEqual(
        trade_model_simulation_movement.getParentValue().getParentValue() \
            .getTotalPrice() * self.default_tax_ratio,
        trade_model_simulation_movement.getTotalPrice()
      )

      self.assertEqual(
        business_path,
        trade_model_simulation_movement.getCausalityValue()
      )

      self.assertEqual(
        price_currency,
        trade_model_simulation_movement.getPriceCurrencyValue()
      )

      self.assertSameSet(
        [],
        trade_model_simulation_movement.getBaseContributionList()
      )

      self.assertSameSet(
        ['base_amount/tax'],
        trade_model_simulation_movement.getBaseApplicationList()
      )
      self.checkInvoiceTransactionRule(trade_model_simulation_movement)

      # TODO:
      #  * trade_phase ???
      #  * arrow
      #  * dates

  def checkInvoiceTransactionRule(self, trade_model_simulation_movement):
    invoice_transaction_rule_list = trade_model_simulation_movement\
        .objectValues()
    self.assertEquals(1, len(invoice_transaction_rule_list))
    invoice_transaction_rule = invoice_transaction_rule_list[0]
    self.assertEqual('Invoice Transaction Rule',
        invoice_transaction_rule.getSpecialiseValue().getPortalType())

    invoice_transaction_simulation_movement_list = invoice_transaction_rule \
        .objectValues()

    self.assertEqual(2, len(invoice_transaction_simulation_movement_list))

    for movement in invoice_transaction_simulation_movement_list:
      self.assertEqual(abs(movement.getQuantity()),
          abs(trade_model_simulation_movement.getTotalPrice()))

  def stepFillOrder(self, sequence=None, **kw):
    order = sequence.get('order')
    price_currency = sequence.get('price_currency')
    source = sequence.get('source')
    destination = sequence.get('destination')
    source_section = sequence.get('source_section')
    destination_section = sequence.get('destination_section')
    self.assertNotEqual(None, price_currency)
    self.assertNotEqual(None, source)
    self.assertNotEqual(None, destination)
    self.assertNotEqual(None, source_section)
    self.assertNotEqual(None, destination_section)
    order.edit(
        source_value=source,
        destination_value=destination,
        source_section_value=source_section,
        destination_section_value=destination_section,
        start_date=self.order_date,
        price_currency_value = price_currency)

  def createResource(self, portal_type, **kw):
    module = self.portal.getDefaultModule(portal_type=portal_type)
    return module.newContent(portal_type=portal_type, **kw)

  def stepCreatePriceCurrency(self, sequence=None, **kw):
    sequence.edit(price_currency = self.createResource('Currency', \
        title='Currency', base_unit_quantity=self.base_unit_quantity))

  def stepCreateProductTaxed(self, sequence=None, **kw):
    sequence.edit(product_taxed = self.createResource('Product',
      title='Product Taxed',
      base_contribution=['base_amount/tax'],
      use='normal',
    ))

  def stepCreateProductDiscounted(self, sequence=None, **kw):
    sequence.edit(product_discounted = self.createResource('Product',
      title='Product Discounted',
      base_contribution=['base_amount/discount'],
      use='normal',
    ))

  def stepCreateProductDiscountedTaxed(self, sequence=None, **kw):
    sequence.edit(product_discounted_taxed = self.createResource('Product',
      title='Product Discounted & Taxed',
      base_contribution=['base_amount/discount', 'base_amount/tax'],
      use='normal',
    ))

  def stepCreateServiceTax(self, sequence=None, **kw):
    sequence.edit(service_tax = self.createResource('Service',
      title='Tax',
      use='tax',
    ))

  def stepCreateServiceDiscount(self, sequence=None, **kw):
    sequence.edit(service_discount = self.createResource('Service',
      title='Discount',
      use='discount',
    ))

  def createTradeCondition(self):
    module = self.portal.getDefaultModule(
        portal_type=self.trade_condition_portal_type)
    trade_condition = module.newContent(
        portal_type=self.trade_condition_portal_type,
        title=self.id())
    return trade_condition

  def stepCreateTradeCondition(self, sequence=None, **kw):
    sequence.edit(trade_condition = self.createTradeCondition())

  def stepCreateInvoiceLine(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    invoice_line = invoice.newContent(portal_type=self.invoice_line_portal_type)
    sequence.edit(invoice_line = invoice_line)

  def stepCreateOrderLine(self, sequence=None, **kw):
    order = sequence.get('order')
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    sequence.edit(order_line = order_line)

  def stepGetInvoiceLineDiscounted(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    resource = sequence.get('product_discounted')
    self.assertNotEqual(None, resource)
    sequence.edit(invoice_line_discounted = [m for m in
      invoice.getMovementList() if m.getResourceValue() == resource][0])

  def stepGetInvoiceLineDiscountedTaxed(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    resource = sequence.get('product_discounted_taxed')
    self.assertNotEqual(None, resource)
    sequence.edit(invoice_line_discounted_taxed = [m for m in
      invoice.getMovementList() if m.getResourceValue() == resource][0])

  def stepGetInvoiceLineTaxed(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    resource = sequence.get('product_taxed')
    self.assertNotEqual(None, resource)
    sequence.edit(invoice_line_taxed = [m for m in
      invoice.getMovementList() if m.getResourceValue() == resource][0])

  def stepModifyQuantityInvoiceLineTaxed(self, sequence=None, **kw):
    invoice_line = sequence.get('invoice_line_taxed')
    invoice_line.edit(
      quantity=invoice_line.getQuantity() * \
          self.modified_invoice_line_quantity_ratio,
    )

  def stepModifyQuantityInvoiceLineDiscounted(self, sequence=None, **kw):
    invoice_line = sequence.get('invoice_line_discounted')
    invoice_line.edit(
      quantity=invoice_line.getQuantity() * \
          self.modified_invoice_line_quantity_ratio,
    )

  def stepModifyQuantityInvoiceLineDiscountedTaxed(self, sequence=None, **kw):
    invoice_line = sequence.get('invoice_line_discounted_taxed')
    invoice_line.edit(
      quantity=invoice_line.getQuantity() * \
          self.modified_invoice_line_quantity_ratio,
    )

  def stepModifyAgainOrderLineTaxed(self, sequence=None, **kw):
    order_line = sequence.get('order_line_taxed')
    order_line.edit(
      price=order_line.getPrice() * self.modified_order_line_price_ratio,
      quantity=order_line.getQuantity() * \
          self.modified_order_line_quantity_ratio,
    )

  def stepModifyAgainOrderLineDiscounted(self, sequence=None, **kw):
    order_line = sequence.get('order_line_discounted')
    order_line.edit(
      price=order_line.getPrice() * self.modified_order_line_price_ratio,
      quantity=order_line.getQuantity() * \
          self.modified_order_line_quantity_ratio,
    )

  def stepModifyAgainOrderLineDiscountedTaxed(self, sequence=None, **kw):
    order_line = sequence.get('order_line_discounted_taxed')
    order_line.edit(
      price=order_line.getPrice() * self.modified_order_line_price_ratio,
      quantity=order_line.getQuantity() * \
          self.modified_order_line_quantity_ratio,
    )

  def stepModifyOrderLineTaxed(self, sequence=None, **kw):
    order_line = sequence.get('order_line')
    resource = sequence.get('product_taxed')
    self.assertNotEqual(None, resource)
    order_line.edit(
      price=1.0,
      quantity=2.0,
      resource_value=resource
    )
    sequence.edit(
      order_line = None,
      order_line_taxed = order_line
    )

  def stepModifyOrderLineDiscounted(self, sequence=None, **kw):
    order_line = sequence.get('order_line')
    resource = sequence.get('product_discounted')
    self.assertNotEqual(None, resource)
    order_line.edit(
      price=3.0,
      quantity=4.0,
      resource_value=resource
    )
    sequence.edit(
      order_line = None,
      order_line_discounted = order_line
    )

  def stepModifyOrderLineDiscountedTaxed(self, sequence=None, **kw):
    order_line = sequence.get('order_line')
    resource = sequence.get('product_discounted_taxed')
    self.assertNotEqual(None, resource)
    order_line.edit(
      price=5.0,
      quantity=6.0,
      resource_value=resource
    )
    sequence.edit(
      order_line = None,
      order_line_discounted_taxed = order_line
    )

  def stepModifyInvoiceLineTaxed(self, sequence=None, **kw):
    invoice_line = sequence.get('invoice_line')
    resource = sequence.get('product_taxed')
    self.assertNotEqual(None, resource)
    invoice_line.edit(
      price=1.0,
      quantity=2.0,
      resource_value=resource
    )
    sequence.edit(
      invoice_line = None,
      invoice_line_taxed = invoice_line
    )

  def stepModifyInvoiceLineDiscounted(self, sequence=None, **kw):
    invoice_line = sequence.get('invoice_line')
    resource = sequence.get('product_discounted')
    self.assertNotEqual(None, resource)
    invoice_line.edit(
      price=3.0,
      quantity=4.0,
      resource_value=resource
    )
    sequence.edit(
      invoice_line = None,
      invoice_line_discounted = invoice_line
    )

  def stepModifyInvoiceLineDiscountedTaxed(self, sequence=None, **kw):
    invoice_line = sequence.get('invoice_line')
    resource = sequence.get('product_discounted_taxed')
    self.assertNotEqual(None, resource)
    invoice_line.edit(
      price=5.0,
      quantity=6.0,
      resource_value=resource
    )
    sequence.edit(
      invoice_line = None,
      invoice_line_discounted_taxed = invoice_line
    )

  def createTradeModelLine(self, document, **kw):
    return document.newContent(
        portal_type='Trade Model Line',
        **kw)

  def stepOrderCreateTradeModelLine(self, sequence=None, **kw):
    order = sequence.get('order')
    sequence.edit(trade_model_line = self.createTradeModelLine(order))

  def stepCreateTradeModelLine(self, sequence=None, **kw):
    trade_condition = sequence.get('trade_condition')
    sequence.edit(
      trade_model_line = self.createTradeModelLine(trade_condition))

  def stepSpecialiseTradeConditionWithBusinessProcess(self, sequence=None,
      **kw):
    business_process = sequence.get('business_process')
    trade_condition = sequence.get('trade_condition')
    self.assertNotEqual(None, business_process)
    trade_condition.setSpecialiseValue(business_process)

  def stepModifyTradeModelLineNewDiscount(self, sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_discount = sequence.get('service_discount')

    trade_model_line.edit(
      price=self.new_discount_ratio,
      base_application='base_amount/discount',
      base_contribution='base_amount/tax',
      trade_phase='default/discount',
      resource_value=service_discount,
      reference='service_discount',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_discount = trade_model_line
    )

  def stepModifyTradeModelLineDiscount(self, sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_discount = sequence.get('service_discount')

    trade_model_line.edit(
      price=self.default_discount_ratio,
      base_application='base_amount/discount',
      base_contribution='base_amount/tax',
      trade_phase='default/discount',
      resource_value=service_discount,
      reference='discount',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_discount = trade_model_line
    )

  def stepModifyTradeModelLineTotalDiscount(self, sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_discount = sequence.get('service_discount')

    trade_model_line.edit(
      price=0.8,
      base_application='base_amount/total_discount',
      trade_phase='default/discount',
      resource_value=service_discount,
      reference='total_discount',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_discount = trade_model_line
    )

  def stepModifyTradeModelLineDiscountContributingToTotalDiscount(self,
      sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_discount = sequence.get('service_discount')

    trade_model_line.edit(
      price=0.32,
      base_application='base_amount/discount',
      base_contribution='base_amount/total_discount',
      trade_phase='default/discount',
      resource_value=service_discount,
      reference='total_dicount_2',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_discount = trade_model_line
    )

  def stepModifyTradeModelLineNewTax(self, sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_tax = sequence.get('service_tax')

    trade_model_line.edit(
      price=self.new_tax_ratio,
      base_application='base_amount/tax',
      trade_phase='default/tax',
      resource_value=service_tax,
      reference='tax_2',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_tax = trade_model_line
    )

  def stepModifyTradeModelLineTax(self, sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_tax = sequence.get('service_tax')

    trade_model_line.edit(
      price=self.default_tax_ratio,
      base_application='base_amount/tax',
      trade_phase='default/tax',
      resource_value=service_tax,
      reference='tax',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_tax = trade_model_line
    )

  def stepModifyTradeModelLineTotalTax(self, sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_tax = sequence.get('service_tax')

    trade_model_line.edit(
      price=0.12,
      base_application='base_amount/total_tax',
      base_contribution='base_amount/total_discount',
      trade_phase='default/tax',
      resource_value=service_tax,
      reference='tax_3',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_tax = trade_model_line
    )

  def stepModifyTradeModelLineTaxContributingToTotalTax(self,
      sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_tax = sequence.get('service_tax')

    trade_model_line.edit(
      price=0.2,
      base_application='base_amount/tax',
      base_contribution='base_amount/total_tax',
      trade_phase='default/tax',
      resource_value=service_tax,
      reference='service_tax',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_tax = trade_model_line
    )

  def stepModifyTradeModelLineTaxContributingToTotalTax2(self,
      sequence=None, **kw):
    trade_model_line = sequence.get('trade_model_line')
    service_tax = sequence.get('service_tax')

    trade_model_line.edit(
      price=0.2,
      base_application='base_amount/tax',
      base_contribution='base_amount/total_tax',
      trade_phase='default/tax',
      resource_value=service_tax,
      reference='service_tax_2',
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_tax = trade_model_line
    )

  def stepUpdateAggregatedAmountListOnOrder(self,
      sequence=None, **kw):
    order = sequence.get('order')
    order.Delivery_updateAggregatedAmountList(batch_mode=1)

  def stepCheckOrderLineTaxedAggregatedAmountList(self, sequence=None, **kw):
    order_line = sequence.get('order_line_taxed')
    trade_condition = sequence.get('trade_condition')
    trade_model_line_tax = sequence.get('trade_model_line_tax')
    amount_list = trade_condition.getAggregatedAmountList(order_line)

    self.assertEquals(1, len(amount_list))
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']
    self.assertEquals(1, len(tax_amount_list))

    tax_amount = tax_amount_list[0]

    self.assertEqual(tax_amount.getReference(),
        trade_model_line_tax.getReference())
    self.assertSameSet(['base_amount/tax'],
        tax_amount.getBaseApplicationList())
    self.assertSameSet([], tax_amount.getBaseContributionList())

    self.assertEqual(order_line.getTotalPrice() * self.default_tax_ratio,
        tax_amount.getTotalPrice())

  def stepCheckOrderLineDiscountedTaxedAggregatedAmountList(self,
      sequence=None, **kw):
    order_line = sequence.get('order_line_discounted_taxed')
    trade_condition = sequence.get('trade_condition')
    trade_model_line_discount = sequence.get('trade_model_line_discount')
    trade_model_line_tax = sequence.get('trade_model_line_tax')
    amount_list = trade_condition.getAggregatedAmountList(order_line)

    self.assertEquals(2, len(amount_list))
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']
    self.assertEquals(1, len(tax_amount_list))
    tax_amount = tax_amount_list[0]

    discount_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/discount']
    self.assertEquals(1, len(discount_amount_list))

    discount_amount = discount_amount_list[0]

    self.assertEqual(tax_amount.getReference(),
        trade_model_line_tax.getReference())
    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())
    self.assertSameSet([], tax_amount.getBaseContributionList())

    self.assertEqual(discount_amount.getReference(),
        trade_model_line_discount.getReference())
    self.assertSameSet(['base_amount/discount'], discount_amount. \
        getBaseApplicationList())
    self.assertSameSet(['base_amount/tax'], discount_amount. \
        getBaseContributionList())

    self.assertEqual(order_line.getTotalPrice() * \
        self.default_discount_ratio, discount_amount.getTotalPrice())

    self.assertEqual((order_line.getTotalPrice() + discount_amount. \
        getTotalPrice()) * self.default_tax_ratio,
        tax_amount.getTotalPrice())

  def stepCheckOrderLineDiscountedAggregatedAmountList(self, sequence=None,
      **kw):
    order_line = sequence.get('order_line_discounted')
    trade_condition = sequence.get('trade_condition')
    trade_model_line_discount = sequence.get('trade_model_line_discount')
    amount_list = trade_condition.getAggregatedAmountList(order_line)

    self.assertEquals(2, len(amount_list))
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']
    self.assertEquals(1, len(tax_amount_list))
    tax_amount = tax_amount_list[0]

    discount_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/discount']
    self.assertEquals(1, len(discount_amount_list))

    discount_amount = discount_amount_list[0]

    self.assertEqual(discount_amount.getReference(),
        trade_model_line_discount.getReference())
    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())
    self.assertSameSet([], tax_amount.getBaseContributionList())

    self.assertSameSet(['base_amount/discount'], discount_amount. \
        getBaseApplicationList())
    self.assertSameSet(['base_amount/tax'], discount_amount. \
        getBaseContributionList())

    self.assertEqual(order_line.getTotalPrice() * \
        self.default_discount_ratio, discount_amount.getTotalPrice())

    # below tax is applied only to discount part
    self.assertEqual(discount_amount.getTotalPrice() * self.default_tax_ratio,
        tax_amount.getTotalPrice())

  def stepCheckOrderComplexTradeConditionAggregatedAmountList(self,
      sequence=None, **kw):
    trade_condition = sequence.get('trade_condition')
    order = sequence.get('order')
    order_line_discounted = sequence.get('order_line_discounted')
    order_line_discounted_taxed = sequence.get('order_line_discounted_taxed')
    order_line_taxed = sequence.get('order_line_taxed')
    trade_model_line_tax = sequence.get('trade_model_line_tax')
    trade_model_line_discount = sequence.get('trade_model_line_discount')

    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEquals(2, len(amount_list))
    discount_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/discount']
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']

    self.assertEquals(1, len(discount_amount_list))
    self.assertEquals(1, len(tax_amount_list))

    discount_amount = discount_amount_list[0]
    tax_amount = tax_amount_list[0]

    self.assertEqual(discount_amount.getReference(),
        trade_model_line_discount.getReference())
    self.assertSameSet(['base_amount/discount'], discount_amount. \
        getBaseApplicationList())

    self.assertSameSet(['base_amount/tax'], discount_amount. \
        getBaseContributionList())

    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())

    self.assertSameSet([], tax_amount.getBaseContributionList())
    self.assertEqual(tax_amount.getReference(),
        trade_model_line_tax.getReference())

    self.assertEqual(
      discount_amount.getTotalPrice(),
      (order_line_discounted.getTotalPrice()
        + order_line_discounted_taxed.getTotalPrice() )
      * self.default_discount_ratio
    )

    self.assertEqual(
      tax_amount.getTotalPrice(),
      (order_line_taxed.getTotalPrice()
        + order_line_discounted_taxed.getTotalPrice()
        + discount_amount.getTotalPrice()) * self.default_tax_ratio
    )

  def stepCheckAggregatedAmountListWithComplexBaseContributionBaseApplication(self,
      sequence=None, **kw):
    trade_condition = sequence.get('trade_condition')
    order = sequence.get('order')
    order_line_discounted = sequence.get('order_line_discounted')
    order_line_discounted_taxed = sequence.get('order_line_discounted_taxed')
    order_line_taxed = sequence.get('order_line_taxed')

    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEquals(5, len(amount_list))
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']
    total_tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/total_tax']
    discount_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/discount']
    total_discount_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/total_discount']

    self.assertEquals(2, len(tax_amount_list))
    self.assertEquals(1, len(total_tax_amount_list))
    self.assertEquals(1, len(discount_amount_list))
    self.assertEquals(1, len(total_discount_amount_list))

    total_tax_amount = total_tax_amount_list[0]
    discount_amount = discount_amount_list[0]
    total_discount_amount = total_discount_amount_list[0]

    self.assertSameSet(['base_amount/total_tax'], total_tax_amount. \
        getBaseApplicationList())
    self.assertSameSet(['base_amount/total_discount'], total_tax_amount. \
        getBaseContributionList())

    self.assertSameSet(['base_amount/discount'], discount_amount. \
        getBaseApplicationList())
    self.assertSameSet(['base_amount/total_discount'], discount_amount. \
        getBaseContributionList())

    self.assertSameSet(['base_amount/total_discount'], total_discount_amount. \
        getBaseApplicationList())
    self.assertSameSet([], total_discount_amount.getBaseContributionList())

    for tax_amount in tax_amount_list:
      self.assertSameSet(['base_amount/tax'], tax_amount. \
          getBaseApplicationList())
      self.assertSameSet(['base_amount/total_tax'], tax_amount. \
          getBaseContributionList())

    for tax_amount in tax_amount_list:
      self.assertEqual(
        tax_amount.getTotalPrice(),
        order_line_taxed.getTotalPrice() * 0.2
      )

    self.assertEqual(
      total_tax_amount.getTotalPrice(),
      (order_line_taxed.getTotalPrice() * 0.2) * 2 * 0.12
    )

    self.assertEqual(
      discount_amount.getTotalPrice(),
      order_line_discounted.getTotalPrice() * 0.32
    )

    self.assertEqual(
      total_discount_amount.getTotalPrice(),
      ((order_line_taxed.getTotalPrice() * 0.2) * 2 * 0.12 + \
      order_line_discounted.getTotalPrice() * 0.32) * 0.8
    )

class TestBPMTestCases(TestBPMMixin):
  COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING = """
              CreateServiceTax
              CreateServiceDiscount
              CreatePriceCurrency
              CreateProductDiscounted
              CreateProductTaxed
              CreateProductDiscountedTaxed
              CreateSource
              CreateSourceSection
              CreateDestination
              CreateDestinationSection
              Tic
  """

  AGGREGATED_AMOUNT_LIST_CHECK_SEQUENCE_STRING = """
              CheckOrderComplexTradeConditionAggregatedAmountList
              CheckOrderLineTaxedAggregatedAmountList
              CheckOrderLineDiscountedTaxedAggregatedAmountList
              CheckOrderLineDiscountedAggregatedAmountList
  """

  AGGREGATED_AMOUNT_LIST_COMMON_SEQUENCE_STRING = \
      COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateBusinessProcess
              CreateBusinessState
              ModifyBusinessStateTaxed
              CreateBusinessState
              ModifyBusinessStateInvoiced
              CreateBusinessPath
              ModifyBusinessPathTaxing
              CreateBusinessPath
              ModifyBusinessPathDiscounting
              CreateTradeCondition
              SpecialiseTradeConditionWithBusinessProcess
              CreateTradeModelLine
              ModifyTradeModelLineTax
              CreateTradeModelLine
              ModifyTradeModelLineDiscount
              Tic
              CreateOrder
              SpecialiseOrderTradeCondition
              FillOrder
              Tic
              CreateOrderLine
              ModifyOrderLineTaxed
              CreateOrderLine
              ModifyOrderLineDiscounted
              CreateOrderLine
              ModifyOrderLineDiscountedTaxed
              Tic
  """ + AGGREGATED_AMOUNT_LIST_CHECK_SEQUENCE_STRING

  def test_TradeConditionTradeModelLineCircularComposition(self):
    """
      If Trade Condition is specialised by another Trade Condition they
      Trade Model Lines shall be merged.
    """
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValue(trade_condition_2)
    trade_condition_2.setSpecialiseValue(trade_condition_1)

    from Products.ERP5Type.Document.TradeCondition import CircularException
    self.assertRaises(
      CircularException,
      trade_condition_1.getTradeModelLineComposedList
    )

  def test_TradeConditionTradeModelLineBasicComposition(self):
    """
      If Trade Condition is specialised by another Trade Condition they
      Trade Model Lines shall be merged.
    """
    service_1 = self.createResource('Service')
    service_2 = self.createResource('Service')

    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValue(trade_condition_2)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        resource_value = service_1)

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        resource_value = service_2)

    self.assertSameSet(
      [trade_condition_1_trade_model_line,
        trade_condition_2_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

  def test_findSpecialiseValueList(self):
    '''
      check that findSpecialiseValueList is able to return all the inheritance
      model tree using Depth-first search

                                  trade_condition_1
                                    /           \
                                   /             \
                                  /               \
                       trade_condition_2       trade_condition_3
                               |
                               |
                               |
                        trade_condition_4

       according to Depth-first search algorihm, result of this graph should be
       [trade_condition_1, trade_condition_2, trade_condition_3,
       trade_condition_4]
    '''
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()
    trade_condition_3 = self.createTradeCondition()
    trade_condition_4 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValueList((trade_condition_2,
      trade_condition_3))
    trade_condition_2.setSpecialiseValue(trade_condition_4)

    speciliase_value_list = trade_condition_1.findSpecialiseValueList(context=\
        trade_condition_1)
    self.assertEquals(len(speciliase_value_list), 4)
    self.assertEquals(
      [trade_condition_1, trade_condition_2, trade_condition_3,
       trade_condition_4], speciliase_value_list)

  def test_TradeConditionTradeModelLineBasicCompositionWithOrder(self):
    """
      If Trade Condition is specialised by another Trade Condition they
      Trade Model Lines shall be merged.
    """
    service_1 = self.createResource('Service')
    service_2 = self.createResource('Service')
    service_3 = self.createResource('Service')

    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()
    order = self.createOrder()

    trade_condition_1.setSpecialiseValue(trade_condition_2)
    order.setSpecialiseValue(trade_condition_1)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        resource_value = service_1)

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        resource_value = service_2)

    order_trade_model_line = self.createTradeModelLine(
        order,
        resource_value = service_3)

    self.assertSameSet(
      [trade_condition_1_trade_model_line, trade_condition_2_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

    self.assertSameSet(
      [trade_condition_1_trade_model_line, trade_condition_2_trade_model_line,
        order_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList(context=order)
    )

  def test_TradeConditionTradeModelLineResourceIsShadowingCompositionWithOrder(self):
    """
      If Trade Condition is specialised by another Trade Condition they
      Trade Model Lines shall be merged.
    """
    service_1 = self.createResource('Service')
    service_2 = self.createResource('Service')

    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()
    order = self.createOrder()

    trade_condition_1.setSpecialiseValue(trade_condition_2)
    order.setSpecialiseValue(trade_condition_1)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        resource_value = service_1,
        reference = 'A')

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        resource_value = service_2,
        reference = 'B')

    order_trade_model_line = self.createTradeModelLine(
        order,
        resource_value = service_2,
        reference = 'B')

    self.assertSameSet(
      [trade_condition_1_trade_model_line,
        trade_condition_2_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

    self.assertSameSet(
      [trade_condition_1_trade_model_line, order_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList(context=order)
    )

  def test_TradeConditionTradeModelLineResourceIsShadowingComposition(self):
    """
      If Trade Condition is specialised by another Trade Condition
      and resource is repeated, only first Trade Model Line shall be returned.
    """
    service = self.createResource('Service')

    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValue(trade_condition_2)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        resource_value = service,
        reference = 'A')

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        resource_value = service,
        reference = 'A')

    self.assertSameSet(
      [trade_condition_1_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

  def test_getTradeModelLineComposedList(self):
    """Test that list of contribution/application relations is sorted to do easy traversal

    Let assume such graph of contribution/application dependency:

    D -----> B
          /   \
    E ---/     > A
              /
    F -----> C
          /
    G ---/

    It shall return list which is sorted like:
      * (DE) B (FG) C A
        or
      * (FG) C (DE) B A
    where everything in parenthesis can be not sorted
    """
    trade_condition = self.createTradeCondition()

    A = self.createTradeModelLine(trade_condition, reference='A',
        base_application_list=['base_amount/total'])

    B = self.createTradeModelLine(trade_condition, reference='B',
        base_contribution_list=['base_amount/total'],
        base_application_list=['base_amount/total_tax'])

    C = self.createTradeModelLine(trade_condition, reference='C',
        base_contribution_list=['base_amount/total'],
        base_application_list=['base_amount/total_discount'])

    D = self.createTradeModelLine(trade_condition, reference='D',
        base_contribution_list=['base_amount/total_tax'],
        base_application_list=['base_amount/tax'])

    E = self.createTradeModelLine(trade_condition, reference='E',
        base_contribution_list=['base_amount/total_tax'],
        base_application_list=['base_amount/tax'])

    F = self.createTradeModelLine(trade_condition, reference='F',
        base_contribution_list=['base_amount/total_discount'],
        base_application_list=['base_amount/discount'])

    G = self.createTradeModelLine(trade_condition, reference='G',
        base_contribution_list=['base_amount/total_discount'],
        base_application_list=['base_amount/discount'])

    trade_model_line_list = trade_condition.getTradeModelLineComposedList()

    # XXX: This is only one good possible sorting
    self.assertEquals(sorted([q.getRelativeUrl() for q in trade_model_line_list]),
        sorted([q.getRelativeUrl() for q in [D, E, B, F, G, C, A]]))

  def test_getAggregatedAmountList(self):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines
    """
    sequence_list = SequenceList()
    sequence_string = self.AGGREGATED_AMOUNT_LIST_COMMON_SEQUENCE_STRING

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING = \
      COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateBusinessProcess
              CreateBusinessState
              ModifyBusinessStateTaxed
              CreateBusinessState
              ModifyBusinessStateInvoiced
              CreateBusinessPath
              ModifyBusinessPathTaxing
              CreateBusinessPath
              ModifyBusinessPathDiscounting
              CreateTradeCondition
              SpecialiseTradeConditionWithBusinessProcess
              CreateTradeModelLine
              ModifyTradeModelLineTax
              Tic
              CreateOrder
              OrderCreateTradeModelLine
              ModifyTradeModelLineDiscount
              SpecialiseOrderTradeCondition
              FillOrder
              Tic
              CreateOrderLine
              ModifyOrderLineTaxed
              CreateOrderLine
              ModifyOrderLineDiscounted
              CreateOrderLine
              ModifyOrderLineDiscountedTaxed
              Tic
    """ + AGGREGATED_AMOUNT_LIST_CHECK_SEQUENCE_STRING

  def test_getAggregatedAmountListOrderSpecialise(self):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines and order itself defines Trade Model Line
    """
    sequence_list = SequenceList()
    sequence_string = self\
        .ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_getAggregatedAmountList_afterUpdateAggregatedAmountList(self):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines

      Check if it is stable if updateAggregatedAmountList was invoked.

      Note: This test assumes, that somethings contributes after update, shall
            be rewritten in a way, that adds explicitly movement which shall
            not be aggregated.
    """
    sequence_list = SequenceList()
    sequence_string = self.AGGREGATED_AMOUNT_LIST_COMMON_SEQUENCE_STRING + """
              UpdateAggregatedAmountListOnOrder
              Tic
    """ + self.AGGREGATED_AMOUNT_LIST_CHECK_SEQUENCE_STRING

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING = """
              CheckOrderLineTaxedSimulation
              CheckOrderLineDiscountedSimulation
              CheckOrderLineDiscountedTaxedSimulation
  """
  TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING = \
      AGGREGATED_AMOUNT_LIST_COMMON_SEQUENCE_STRING + """
              Tic
              PlanOrder
              Tic
  """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING

  def test_TradeModelRuleSimulationExpand(self):
    """Tests tree of simulations from Trade Model Rule"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationReexpand(self):
    """Tests tree of simulations from Trade Model Rule with reexpanding"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING + """
              ModifyAgainOrderLineTaxed
              ModifyAgainOrderLineDiscounted
              ModifyAgainOrderLineDiscountedTaxed
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING = \
      ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING + """
              Tic
              PlanOrder
              Tic
  """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING

  def test_TradeModelRuleSimulationExpandOrderSpecialise(self):
    """Tests tree of simulations from Trade Model Rule"""
    sequence_list = SequenceList()
    sequence_string = self \
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationReexpandOrderSpecialise(self):
    """Tests tree of simulations from Trade Model Rule with reexpanding"""
    sequence_list = SequenceList()
    sequence_string = self \
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING+ """
              ModifyAgainOrderLineTaxed
              ModifyAgainOrderLineDiscounted
              ModifyAgainOrderLineDiscountedTaxed
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationWithoutBPM(self):
    """Tests tree of simulations from Trade Model Rule when there is no BPM"""
    sequence_list = SequenceList()
    sequence_string = self.COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateTradeCondition
              CreateTradeModelLine
              ModifyTradeModelLineTax
              Tic
              CreateOrder
              SpecialiseOrderTradeCondition
              FillOrder
              Tic
              CreateOrderLine
              ModifyOrderLineTaxed
              Tic
              PlanOrder
              Tic
              CheckOrderTaxNoSimulation
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationWithoutTradeCondition(self):
    """Tests tree of simulations from Trade Model Rule when there is no Trade Condition"""
    sequence_list = SequenceList()
    sequence_string = self.COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateOrder
              FillOrder
              Tic
              CreateOrderLine
              ModifyOrderLineTaxed
              Tic
              PlanOrder
              Tic
              CheckOrderTaxNoSimulation
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoice(self):
    """Check that invoice lines on invoice are correctly set"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceNewTradeCondition(self):
    """Check that after changing trade condition invoice is not diverged"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements

              SetTradeConditionOld

              CreateTradeCondition
              SpecialiseTradeConditionWithBusinessProcess
              CreateTradeModelLine
              ModifyTradeModelLineNewTax
              CreateTradeModelLine
              ModifyTradeModelLineNewDiscount
              Tic

              SpecialiseInvoiceTradeCondition
              Tic
              CheckInvoiceCausalityStateSolved
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceNewInvoiceLineSupport(self):
    """Check how is supported addition of invoice line to invoice build from order"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements

              CreateInvoiceLine
              ModifyInvoiceLineDiscounted
              CreateInvoiceLine
              ModifyInvoiceLineDiscountedTaxed
              CreateInvoiceLine
              ModifyInvoiceLineTaxed

              Tic

              CheckInvoiceCausalityStateSolved

              StartInvoice
              Tic
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceAccountingMovements
              StopInvoice
              DeliverInvoice
              Tic
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceInvoiceLineModifyDivergencyAndSolving(self):
    """Check that after changing invoice line invoice is properly diverged and it is possible to solve"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements

              GetInvoiceLineDiscounted
              GetInvoiceLineDiscountedTaxed
              GetInvoiceLineTaxed

              ModifyQuantityInvoiceLineDiscounted
              ModifyQuantityInvoiceLineDiscountedTaxed
              ModifyQuantityInvoiceLineTaxed
              Tic
              CheckInvoiceCausalityStateDiverged
              AcceptDecisionQuantityInvoice
              Tic
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceBuildInvoiceTransactionLines(self):
    """Check that having properly configured invoice transaction rule it invoice transaction lines are nicely generated and have proper amounts"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements

              StartInvoice
              Tic
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceAccountingMovements
              StopInvoice
              DeliverInvoice
              Tic
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  PACKING_LIST_SPLIT_INVOICE_BUILD_SEQUENCE_STRING = \
      TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING + """
              ConfirmOrder
              Tic
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetPackingList
              DecreasePackingListLineListQuantity
              Tic
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              CheckPackingListDiverged
              SplitAndDeferPackingList
              Tic
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetNewPackingList
              PackPackingList
              Tic
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements

              SetNewPackingListAsPackingList
              PackPackingList
              Tic
              StartPackingList
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              StopPackingList
              DeliverPackingList
              Tic
    """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
    """

  def test_TradeModelRuleSimulationPackingListSplitBuildInvoiceBuildDifferentRatio(self):
    """Check building invoice after splitting packing list using different ratio"""
    self.modified_packing_list_line_quantity_ratio = 0.4
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
        self.PACKING_LIST_SPLIT_INVOICE_BUILD_SEQUENCE_STRING)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationPackingListSplitBuildInvoiceBuild(self):
    """Check building invoice after splitting packing list"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
        self.PACKING_LIST_SPLIT_INVOICE_BUILD_SEQUENCE_STRING)
    sequence_list.play(self)

  def test_getAggregatedAmountListWithComplexModelLinesCreateInEasyOrder(self):
    """
    Test the return of getAggregatedAmountList in the case of many model lines
    depending each others. In this test, lines are created in the order of the
    dependancies (it means that if a line A depend of a line B, line B is
    created before A). This is the most easy case.

    Dependance tree :
    ModelLineTaxContributingToTotalTax : A
    ModelLineDiscountContributingToTotalDiscount : B
    ModelLineTaxContributingToTotalTax2 : C
    ModelLineTotalTax : D
    ModelLineTotalDiscount : E

                              D       E
                               \     /
                                \   /
                                 \ /
                                  C      B
                                   \    /
                                    \  /
                                     \/
                                      A
    Model line creation order : E, D, C, B, A
    """
    sequence_list = SequenceList()
    sequence_string = self.COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateBusinessProcess
              CreateBusinessState
              ModifyBusinessStateTaxed
              CreateBusinessState
              ModifyBusinessStateInvoiced
              CreateBusinessPath
              ModifyBusinessPathTaxing
              CreateBusinessPath
              ModifyBusinessPathDiscounting
              CreateTradeCondition
              SpecialiseTradeConditionWithBusinessProcess
              CreateTradeModelLine
              ModifyTradeModelLineTotalDiscount
              CreateTradeModelLine
              ModifyTradeModelLineTotalTax
              CreateTradeModelLine
              ModifyTradeModelLineTaxContributingToTotalTax2
              CreateTradeModelLine
              ModifyTradeModelLineDiscountContributingToTotalDiscount
              CreateTradeModelLine
              ModifyTradeModelLineTaxContributingToTotalTax
              Tic
              CreateOrder
              SpecialiseOrderTradeCondition
              FillOrder
              Tic
              CreateOrderLine
              ModifyOrderLineTaxed
              CreateOrderLine
              ModifyOrderLineDiscounted
              Tic
              CheckAggregatedAmountListWithComplexBaseContributionBaseApplication
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_getAggregatedAmountListWithComplexModelLinesCreateInRandomOrder(self):
    """
    Test the return of getAggregatedAmountList in the case of many model lines
    depending each others. In this test, lines are created in a random order,
    not in the dependancies order (it means that if a line A depend of a 
    line B, line A can be created before line B). getAggregatedAmountList
    should be able to handle this case and redo calculation unill all
    dependancies are satified

    Dependance tree :
    ModelLineTaxContributingToTotalTax : A
    ModelLineDiscountContributingToTotalDiscount : B
    ModelLineTaxContributingToTotalTax2 : C
    ModelLineTotalTax : D
    ModelLineTotalDiscount : E

                              D       E
                               \     /
                                \   /
                                 \ /
                                  C      B
                                   \    /
                                    \  /
                                     \/
                                      A
    Model line creation order : A, C, D, B, E
    """
    sequence_list = SequenceList()
    sequence_string = self.COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateBusinessProcess
              CreateBusinessState
              ModifyBusinessStateTaxed
              CreateBusinessState
              ModifyBusinessStateInvoiced
              CreateBusinessPath
              ModifyBusinessPathTaxing
              CreateBusinessPath
              ModifyBusinessPathDiscounting
              CreateTradeCondition
              SpecialiseTradeConditionWithBusinessProcess
              CreateTradeModelLine
              ModifyTradeModelLineTaxContributingToTotalTax
              CreateTradeModelLine
              ModifyTradeModelLineTaxContributingToTotalTax2
              CreateTradeModelLine
              ModifyTradeModelLineTotalTax
              CreateTradeModelLine
              ModifyTradeModelLineDiscountContributingToTotalDiscount
              CreateTradeModelLine
              ModifyTradeModelLineTotalDiscount
              Tic
              CreateOrder
              SpecialiseOrderTradeCondition
              FillOrder
              Tic
              CreateOrderLine
              ModifyOrderLineTaxed
              CreateOrderLine
              ModifyOrderLineDiscounted
              Tic
              CheckAggregatedAmountListWithComplexBaseContributionBaseApplication
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

class TestBPMSale(TestBPMTestCases):
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  packing_list_portal_type = 'Sale Packing List'
  trade_condition_portal_type = 'Sale Trade Condition'
  trade_model_line_portal_type = 'Trade Model Line'


class TestBPMPurchase(TestBPMTestCases):
  invoice_portal_type = 'Purchase Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  packing_list_portal_type = 'Purchase Packing List'
  trade_condition_portal_type = 'Purchase Trade Condition'
  trade_model_line_portal_type = 'Trade Model Line'


class TestBPMImplementation(TestBPMMixin):
  """Business Process implementation tests"""
  def test_BusinessProcess_getPathValueList(self):
    business_process = self.createBusinessProcess()

    accounting_business_path = business_process.newContent(
        portal_type=self.business_path_portal_type,
        trade_phase='default/accounting')

    delivery_business_path = business_process.newContent(
        portal_type=self.business_path_portal_type,
        trade_phase='default/delivery')

    accounting_delivery_business_path = business_process.newContent(
        portal_type=self.business_path_portal_type,
        trade_phase=('default/accounting', 'default/delivery'))

    self.stepTic()

    self.assertSameSet(
      (accounting_business_path, accounting_delivery_business_path),
      business_process.getPathValueList(trade_phase='default/accounting')
    )

    self.assertSameSet(
      (delivery_business_path, accounting_delivery_business_path),
      business_process.getPathValueList(trade_phase='default/delivery')
    )

    # XXX: Luke: it is ORing not ANDing?
    self.assertSameSet(
      (accounting_delivery_business_path, delivery_business_path,
        accounting_business_path),
      business_process.getPathValueList(trade_phase=('default/delivery',
        'default/accounting'))
    )

  def test_BusinessPathStandardCategoryAccessProvider(self):
    node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    business_path = self.createBusinessPath()
    business_path.setSourceValue(node)
    self.assertEquals(node, business_path.getSourceValue())
    self.assertEquals(node.getRelativeUrl(), business_path.getSource())
    self.assertEquals(node.getRelativeUrl(),
        business_path.getSource(default='something'))

  def test_EmptyBusinessPathStandardCategoryAccessProvider(self):
    business_path = self.createBusinessPath()
    self.assertEquals(None, business_path.getSourceValue())
    self.assertEquals(None, business_path.getSource())
    self.assertEquals('something',
        business_path.getSource(default='something'))

  def test_BuinessPathDynamicCategoryAccessProvider(self):
    node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    business_path = self.createBusinessPath()
    business_path.setSourceMethodId('BusinessPath_getDefaultSourceList')

    context_movement = self.createMovement()
    context_movement.setSourceValue(node)
    self.assertEquals(None, business_path.getSourceValue())
    self.assertEquals(node,
                      business_path.getSourceValue(context=context_movement))
    self.assertEquals(node.getRelativeUrl(),
                      business_path.getSource(context=context_movement))
    self.assertEquals(node.getRelativeUrl(),
      business_path.getSource(context=context_movement, default='something'))

  def test_BuinessPathDynamicCategoryAccessProviderEmptyMovement(self):
    business_path = self.createBusinessPath()
    business_path.setSourceMethodId('BusinessPath_getDefaultSourceList')

    context_movement = self.createMovement()
    self.assertEquals(None, business_path.getSourceValue())
    self.assertEquals(None,
                      business_path.getSourceValue(context=context_movement))
    self.assertEquals(None,
                      business_path.getSource(context=context_movement))
    self.assertEquals('something',
      business_path.getSource(context=context_movement, default='something'))

  def test_BusinessState_getRemainingTradePhaseList(self):
    """
    This test case is described for what trade_phase is remaining after the state.
    In this case, root explanation is path of between "b" and "d", and
    path of between "a" and "b" has a condition which simulation state of
    explanation must be "ordered" to pass the path. (*1)
    But this test case will be passed the condition.

                            (root explanation)
       default/discount     default/invoicing     default/accounting
    a ------------------ b ------------------- d -------------------- e
       (cond="ordered")   \                   /
                           \                 /
          default/delivery  \               / default/payment
                             \             /
                              \           /
                               \         /
                                \       /
                                 \     /
                                  \   /
                                   \ /
                                    c
    """
    # define business process
    business_process = self.createBusinessProcess()
    business_path_a_b = self.createBusinessPath(business_process)
    business_path_b_c = self.createBusinessPath(business_process)
    business_path_b_d = self.createBusinessPath(business_process)
    business_path_c_d = self.createBusinessPath(business_process)
    business_path_d_e = self.createBusinessPath(business_process)
    business_state_a = self.createBusinessState(business_process)
    business_state_b = self.createBusinessState(business_process)
    business_state_c = self.createBusinessState(business_process)
    business_state_d = self.createBusinessState(business_process)
    business_state_e = self.createBusinessState(business_process)
    business_path_a_b.setPredecessorValue(business_state_a)
    business_path_b_c.setPredecessorValue(business_state_b)
    business_path_b_d.setPredecessorValue(business_state_b)
    business_path_c_d.setPredecessorValue(business_state_c)
    business_path_d_e.setPredecessorValue(business_state_d)
    business_path_a_b.setSuccessorValue(business_state_b)
    business_path_b_c.setSuccessorValue(business_state_c)
    business_path_b_d.setSuccessorValue(business_state_d)
    business_path_c_d.setSuccessorValue(business_state_d)
    business_path_d_e.setSuccessorValue(business_state_e)

    # set title for debug
    business_path_a_b.edit(title="a_b")
    business_path_b_c.edit(title="b_c")
    business_path_b_d.edit(title="b_d")
    business_path_c_d.edit(title="c_d")
    business_path_d_e.edit(title="d_e")
    business_state_a.edit(title="a")
    business_state_b.edit(title="b")
    business_state_c.edit(title="c")
    business_state_d.edit(title="d")
    business_state_e.edit(title="e")
    
    # set trade_phase
    business_path_a_b.edit(trade_phase=['default/discount'],
                           completed_state=['ordered']) # (*1)
    business_path_b_c.edit(trade_phase=['default/delivery'])
    business_path_b_d.edit(trade_phase=['default/invoicing'])
    business_path_c_d.edit(trade_phase=['default/payment'])
    business_path_d_e.edit(trade_phase=['default/accounting'])

    # mock order
    order = self.portal.sale_order_module.newContent(portal_type="Sale Order")
    order_line = order.newContent(portal_type="Sale Order Line")

    # make simulation
    order.order()

    self.stepTic()

    applied_rule = order.getCausalityRelatedValue()
    sm = applied_rule.contentValues(portal_type="Simulation Movement")[0]
    sm.edit(causality_value=business_path_a_b)

    # make other movements for each business path
    applied_rule.newContent(portal_type="Simulation Movement",
                            causality_value=business_path_b_c,
                            order_value=order_line)
    applied_rule.newContent(portal_type="Simulation Movement",
                            causality_value=business_path_b_d,
                            order_value=order_line)
    applied_rule.newContent(portal_type="Simulation Movement",
                            causality_value=business_path_c_d,
                            order_value=order_line)
    applied_rule.newContent(portal_type="Simulation Movement",
                            causality_value=business_path_d_e,
                            order_value=order_line)

    self.stepTic()

    trade_phase = self.portal.portal_categories.trade_phase.default

    # assertion which getRemainingTradePhaseList must return category which will be passed
    # discount is passed, business_path_a_b is already completed, because simulation state is "ordered"
    self.assertEquals(set([trade_phase.delivery,
                           trade_phase.invoicing,
                           trade_phase.payment,
                           trade_phase.accounting]),
                      set(business_state_a.getRemainingTradePhaseList(order)))
    self.assertEquals(set([trade_phase.delivery,
                           trade_phase.invoicing,
                           trade_phase.payment,
                           trade_phase.accounting]),
                      set(business_state_b.getRemainingTradePhaseList(order)))
    self.assertEquals(set([trade_phase.payment,
                           trade_phase.accounting]),
                      set(business_state_c.getRemainingTradePhaseList(order)))
    self.assertEquals(set([trade_phase.accounting]),
                      set(business_state_d.getRemainingTradePhaseList(order)))

    # when trade_phase_list is defined in arguments, the result is filtered by base category.
    self.assertEquals(set([trade_phase.delivery,
                           trade_phase.accounting]),
                      set(business_state_a\
                          .getRemainingTradePhaseList(order,
                                                      trade_phase_list=['default/delivery',
                                                                        'default/accounting'])))

  def test_BusinessPath_calculateExpectedDate(self):
    """
    This test case is described for what start/stop date is expected on
    each path by explanation.
    In this case, root explanation is path of between "b" and "d", and
    lead time and wait time is set on each path.
    ("l" is lead time, "w" is wait_time)

    Each path must calculate most early day from getting most longest
    path in the simulation.

    "referential_date" represents for which date have to get of explanation from reality.

                  (root_explanation)
        l:2, w:1         l:3, w:1       l:4, w:2
    a ------------ b -------------- d -------------- e
                    \             /
                     \           /
             l:2, w:1 \         / l:3, w:0
                       \       /
                        \     /
                         \   /
                          \ /
                           c
    """
    # define business process
    business_process = self.createBusinessProcess()
    business_path_a_b = self.createBusinessPath(business_process)
    business_path_b_c = self.createBusinessPath(business_process)
    business_path_b_d = self.createBusinessPath(business_process)
    business_path_c_d = self.createBusinessPath(business_process)
    business_path_d_e = self.createBusinessPath(business_process)
    business_state_a = self.createBusinessState(business_process)
    business_state_b = self.createBusinessState(business_process)
    business_state_c = self.createBusinessState(business_process)
    business_state_d = self.createBusinessState(business_process)
    business_state_e = self.createBusinessState(business_process)
    business_path_a_b.setPredecessorValue(business_state_a)
    business_path_b_c.setPredecessorValue(business_state_b)
    business_path_b_d.setPredecessorValue(business_state_b)
    business_path_c_d.setPredecessorValue(business_state_c)
    business_path_d_e.setPredecessorValue(business_state_d)
    business_path_a_b.setSuccessorValue(business_state_b)
    business_path_b_c.setSuccessorValue(business_state_c)
    business_path_b_d.setSuccessorValue(business_state_d)
    business_path_c_d.setSuccessorValue(business_state_d)
    business_path_d_e.setSuccessorValue(business_state_e)

    business_process.edit(referential_date='stop_date')
    business_state_a.edit(title='a')
    business_state_b.edit(title='b')
    business_state_c.edit(title='c')
    business_state_d.edit(title='d')
    business_state_e.edit(title='e')
    business_path_a_b.edit(title='a_b', lead_time=2, wait_time=1)
    business_path_b_c.edit(title='b_c', lead_time=2, wait_time=1)
    business_path_b_d.edit(title='b_d', lead_time=3, wait_time=1)
    business_path_c_d.edit(title='c_d', lead_time=3, wait_time=0)
    business_path_d_e.edit(title='d_e', lead_time=4, wait_time=2)

    # root explanation
    business_path_b_d.edit(deliverable=True)
    self.stepTic()

    """
    Basic test, lead time of reality and simulation are consistent.
    """
    class Mock:
      def __init__(self, date):
        self.date = date
      def getStartDate(self):
        return self.date
      def getStopDate(self):
        return self.date + 3 # lead time of reality

    base_date = DateTime('2009/04/01 GMT+9')
    mock = Mock(base_date)

    # root explanation.
    self.assertEquals(business_path_b_d.getExpectedStartDate(mock), DateTime('2009/04/01 GMT+9'))
    self.assertEquals(business_path_b_d.getExpectedStopDate(mock), DateTime('2009/04/04 GMT+9'))

    # assertion for each path without root explanation.
    self.assertEquals(business_path_a_b.getExpectedStartDate(mock), DateTime('2009/03/27 GMT+9'))
    self.assertEquals(business_path_a_b.getExpectedStopDate(mock), DateTime('2009/03/29 GMT+9'))
    self.assertEquals(business_path_b_c.getExpectedStartDate(mock), DateTime('2009/03/30 GMT+9'))
    self.assertEquals(business_path_b_c.getExpectedStopDate(mock), DateTime('2009/04/01 GMT+9'))
    self.assertEquals(business_path_c_d.getExpectedStartDate(mock), DateTime('2009/04/01 GMT+9'))
    self.assertEquals(business_path_c_d.getExpectedStopDate(mock), DateTime('2009/04/04 GMT+9'))
    self.assertEquals(business_path_d_e.getExpectedStartDate(mock), DateTime('2009/04/06 GMT+9'))
    self.assertEquals(business_path_d_e.getExpectedStopDate(mock), DateTime('2009/04/10 GMT+9'))

    """
    Test of illegal case, lead time of reality and simulation are inconsistent,
    always reality is taken, but it depends on which date(e.g. start_date and stop_date) is referential.

    How we know which is referential, currently implementation of it can be known by
    BusinessProcess.isStartDateReferential and BusinessProcess.isStopDateReferential.

    In this test case, stop_date on business_path_b_d is referential, because business_path_b_d is
    root explanation and business_process refer to stop_date as referential.

    calculation example(when referential date is 2009/04/06 GMT+9):
    start_date of business_path_b_d = referential_date - 3(lead_time of business_path_b_d)
                                    = 2009/04/06 GMT+9 - 3
                                    = 2009/04/03 GMT+9
    """
    class Mock:
      def __init__(self, date):
        self.date = date
      def getStartDate(self):
        return self.date
      def getStopDate(self):
        return self.date + 5 # changed

    base_date = DateTime('2009/04/01 GMT+9')
    mock = Mock(base_date)

    self.assertEquals(business_path_b_d.getExpectedStartDate(mock), DateTime('2009/04/03 GMT+9'))
    # This is base in this context, because referential_date is 'stop_date'
    self.assertEquals(business_path_b_d.getExpectedStopDate(mock), DateTime('2009/04/06 GMT+9'))

    # assertion for each path without root explanation.
    self.assertEquals(business_path_a_b.getExpectedStartDate(mock), DateTime('2009/03/29 GMT+9'))
    self.assertEquals(business_path_a_b.getExpectedStopDate(mock), DateTime('2009/03/31 GMT+9'))
    self.assertEquals(business_path_b_c.getExpectedStartDate(mock), DateTime('2009/04/01 GMT+9'))
    self.assertEquals(business_path_b_c.getExpectedStopDate(mock), DateTime('2009/04/03 GMT+9'))
    self.assertEquals(business_path_c_d.getExpectedStartDate(mock), DateTime('2009/04/03 GMT+9'))
    self.assertEquals(business_path_c_d.getExpectedStopDate(mock), DateTime('2009/04/06 GMT+9'))
    self.assertEquals(business_path_d_e.getExpectedStartDate(mock), DateTime('2009/04/08 GMT+9'))
    self.assertEquals(business_path_d_e.getExpectedStopDate(mock), DateTime('2009/04/12 GMT+9'))

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBPMSale))
  suite.addTest(unittest.makeSuite(TestBPMPurchase))
  suite.addTest(unittest.makeSuite(TestBPMImplementation))
  return suite
