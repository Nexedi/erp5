# -*- coding: utf8 -*-
##############################################################################
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
import transaction

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager
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

  modified_packing_list_line_quantity_ratio = 0.4

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
      'tax'])
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
    get_transaction().commit()
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

    # XXX for testing purpose only...
    # This builder is not supporting yet deeper simulation tree
    # New one shall be done (decision making with
    # DeliveryCausalityAssignmentMovementGroup), but right now it is enough
    # to support invoice building that way
    sale_invoice_builder, purchase_invoice_builder = self.portal. \
        portal_deliveries.sale_invoice_builder, \
        self.portal.portal_deliveries.purchase_invoice_builder
    delete_id = 'causality_movement_group_on_delivery'
    if getattr(sale_invoice_builder, delete_id, None) is not None:
      sale_invoice_builder.manage_delObjects(ids=[delete_id])
    if getattr(purchase_invoice_builder, delete_id, None) is not None:
      purchase_invoice_builder.manage_delObjects(ids=[delete_id])

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

  def stepCreateOrder(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    order = module.newContent(portal_type=self.order_portal_type)
    sequence.edit(order = order)

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
    invoice_line_tax = sequence.get('invoice_line_tax')
    invoice_line_discount = sequence.get('invoice_line_discount')

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

    self.assertEqual(abs(payable_receivable_line.getTotalPrice()),
        rounded_total_price)

    self.assertEqual(abs(vat_line.getTotalPrice()),
        rounded_tax_price)

    self.assertEquals(abs(income_expense_line.getTotalPrice()),
        rounded_total_price - rounded_tax_price)

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

  def stepCheckInvoiceTradeModelRelatedMovements(self, sequence=None, **kw):
    # movement selection is done by hand, as no API is yet defined
    invoice = sequence.get('invoice')
    trade_condition = sequence.get('trade_condition')
    trade_model_invoice_line_list = [q for q in invoice.getMovementList()
        if q.getResourceValue().getUse() in ('discount','tax')]
    self.assertEqual(2, len(trade_model_invoice_line_list))
    invoice_line_tax = [q for q in trade_model_invoice_line_list if
        q.getResourceValue().getUse() == 'tax' ][0]
    invoice_line_discount = [q for q in trade_model_invoice_line_list if
        q.getResourceValue().getUse() == 'discount' ][0]
    sequence.edit(invoice_line_discount = invoice_line_discount)
    sequence.edit(invoice_line_tax = invoice_line_tax)
    amount_list = trade_condition.getAggregatedAmountList(invoice)
    self.assertEquals(2, len(amount_list))
    discount_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/discount']
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']

    self.assertEquals(1, len(discount_amount_list))
    self.assertEquals(1, len(tax_amount_list))

    discount_amount = discount_amount_list[0]
    tax_amount = tax_amount_list[0]

    self.assertSameSet(discount_amount.getBaseApplicationList(),
        invoice_line_discount.getBaseApplicationList())

    self.assertSameSet(discount_amount.getBaseContributionList(),
        invoice_line_discount.getBaseContributionList())

    self.assertSameSet(tax_amount.getBaseApplicationList(),
        invoice_line_tax.getBaseApplicationList())

    self.assertSameSet(tax_amount.getBaseContributionList(),
        invoice_line_tax.getBaseContributionList())

    self.assertEqual(
      invoice_line_discount.getTotalPrice(),
      discount_amount.getTotalPrice()
    )

    self.assertEqual(
      invoice_line_tax.getTotalPrice(),
      tax_amount.getTotalPrice()
    )

  def stepAcceptDecisionInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    invoice.portal_workflow.doActionFor(invoice,'accept_decision_action')

  def stepCheckInvoiceCausalityStateSolved(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self.assertEqual('solved', invoice.getCausalityState(), invoice.getDivergenceList())

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

      self.checkInvoiceTransactionRule(trade_model_simulation_movement_tax_complex)
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

  def stepCreateTradeCondition(self, sequence=None, **kw):
    module = self.portal.getDefaultModule(
        portal_type=self.trade_condition_portal_type)
    trade_condition = module.newContent(
        portal_type=self.trade_condition_portal_type)

    sequence.edit(trade_condition = trade_condition)

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

  def stepCreateTradeModelLine(self, sequence=None, **kw):
    trade_condition = sequence.get('trade_condition')
    trade_model_line = trade_condition.newContent(
        portal_type='Trade Model Line')
    sequence.edit(trade_model_line = trade_model_line)

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
    amount_list = trade_condition.getAggregatedAmountList(order_line)

    self.assertEquals(1, len(amount_list))
    tax_amount_list = [q for q in amount_list
        if q.getBaseApplication() == 'base_amount/tax']
    self.assertEquals(1, len(tax_amount_list))

    tax_amount = tax_amount_list[0]

    self.assertSameSet(['base_amount/tax'],
        tax_amount.getBaseApplicationList())
    self.assertSameSet([], tax_amount.getBaseContributionList())

    self.assertEqual(order_line.getTotalPrice() * self.default_tax_ratio,
        tax_amount.getTotalPrice())

  def stepCheckOrderLineDiscountedTaxedAggregatedAmountList(self,
      sequence=None, **kw):
    order_line = sequence.get('order_line_discounted_taxed')
    trade_condition = sequence.get('trade_condition')
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

    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())
    self.assertSameSet([], tax_amount.getBaseContributionList())

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

    self.assertSameSet(['base_amount/discount'], discount_amount. \
        getBaseApplicationList())

    self.assertSameSet(['base_amount/tax'], discount_amount. \
        getBaseContributionList())

    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())

    self.assertSameSet([], tax_amount.getBaseContributionList())

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

class TestBPMTestCases(TestBPMMixin):
  common_documents_creation = """
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

  aggregated_amount_list_check = """
              CheckOrderComplexTradeConditionAggregatedAmountList
              CheckOrderLineTaxedAggregatedAmountList
              CheckOrderLineDiscountedTaxedAggregatedAmountList
              CheckOrderLineDiscountedAggregatedAmountList
  """

  aggregated_amount_list_common_sequence_string = \
      common_documents_creation + """
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
  """ + aggregated_amount_list_check

  def test_getAggreagtedAmountList(self):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines
    """
    sequence_list = SequenceList()
    sequence_string = self.aggregated_amount_list_common_sequence_string

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_getAggreagtedAmountList_afterUpdateAggregatedAmountList(self):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines

      Check if it is stable if updateAggregatedAmountList was invoked.

      Note: This test assumes, that somethings contributes after update, shall
            be rewritten in a way, that adds explicitly movement which shall
            not be aggregated.
    """
    sequence_list = SequenceList()
    sequence_string = self.aggregated_amount_list_common_sequence_string + """
              UpdateAggregatedAmountListOnOrder
              Tic
    """ + self.aggregated_amount_list_check

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  aggregated_amount_simulation_check = """
              CheckOrderLineTaxedSimulation
              CheckOrderLineDiscountedSimulation
              CheckOrderLineDiscountedTaxedSimulation
  """
  trade_model_rule_simulation_common_string = \
      aggregated_amount_list_common_sequence_string + """
              Tic
              PlanOrder
              Tic
  """ + aggregated_amount_simulation_check

  def test_TradeModelRuleSimulationExpand(self):
    """Tests tree of simulations from Trade Model Rule"""
    sequence_list = SequenceList()
    sequence_string = self.trade_model_rule_simulation_common_string
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationReexpand(self):
    """Tests tree of simulations from Trade Model Rule with reexpanding"""
    sequence_list = SequenceList()
    sequence_string = self.trade_model_rule_simulation_common_string + """
              ModifyAgainOrderLineTaxed
              ModifyAgainOrderLineDiscounted
              ModifyAgainOrderLineDiscountedTaxed
              Tic
    """ + self.aggregated_amount_simulation_check
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationWithoutBPM(self):
    """Tests tree of simulations from Trade Model Rule when there is no BPM"""
    sequence_list = SequenceList()
    sequence_string = self.common_documents_creation + """
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
    sequence_string = self.common_documents_creation + """
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
    sequence_string = self.trade_model_rule_simulation_common_string
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceNewTradeConditionDivergencyAndSolving(self):
    """Check that after changing trade condition invoice is properly diverged and it is possible to solve"""
    sequence_list = SequenceList()
    sequence_string = self.trade_model_rule_simulation_common_string
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements

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
              SetTradeConditionNew
              GetOldTradeCondition
              CheckInvoiceCausalityStateDiverged
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements

              AdoptPrevisionQuantityInvoice
              Tic

              GetNewTradeCondition
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceNewInvoiceLineSupport(self):
    """Check how is supported addition of invoice line to invoice build from order"""
    raise NotImplementedError('TODO')

  def test_TradeModelRuleSimulationBuildInvoiceInvoiceLineModifyDivergencyAndSolving(self):
    """Check that after changing invoice line invoice is properly diverged and it is possible to solve"""
    sequence_list = SequenceList()
    sequence_string = self.trade_model_rule_simulation_common_string
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements

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
              CheckInvoiceCausalityStateDiverged
              AdoptPrevisionQuantityInvoice
              Tic
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationBuildInvoiceBuildInvoiceTransactionLines(self):
    """Check that having properly configured invoice transaction rule it invoice transaction lines are nicely generated and have proper amounts"""
    sequence_list = SequenceList()
    sequence_string = self.trade_model_rule_simulation_common_string
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetPackingList
              PackPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements

              StartInvoice
              Tic
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements
              CheckInvoiceAccountingMovements
              StopInvoice
              DeliverInvoice
              Tic
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_TradeModelRuleSimulationPackingListSplitBuildInvoiceBuild(self):
    """Check building invoice after splitting packing list"""
    sequence_list = SequenceList()
    sequence_string = self.trade_model_rule_simulation_common_string
    sequence_string += """
              ConfirmOrder
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetPackingList
              DecreasePackingListLineListQuantity
              Tic
    """ + self.aggregated_amount_simulation_check + """
              CheckPackingListDiverged
              SplitAndDeferPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetNewPackingList
              PackPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              StartPackingList
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements

              SetNewPackingListAsPackingList
              PackPackingList
              Tic
              StartPackingList
    """ + self.aggregated_amount_simulation_check + """
              StopPackingList
              DeliverPackingList
              Tic
    """ + self.aggregated_amount_simulation_check + """
              GetInvoice
              CheckInvoiceCausalityStateSolved
              CheckInvoiceNormalMovements
              CheckInvoiceTradeModelRelatedMovements
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

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBPMSale))
  suite.addTest(unittest.makeSuite(TestBPMPurchase))
  suite.addTest(unittest.makeSuite(TestBPMImplementation))
  return suite
