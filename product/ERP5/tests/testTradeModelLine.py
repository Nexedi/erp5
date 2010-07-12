# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#          Fabien Morin <fabien@nexedi.com>
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

from Products.ERP5.tests.testERP5SimulationBPMCore import TestBPMMixin
from Products.ERP5Type.tests.backportUnittest import expectedFailure
from Products.ERP5Type.tests.Sequence import SequenceList
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.utils import createZODBPythonScript

class TestTradeModelLineMixin(TestBPMMixin):
  """Provides methods to implementations sharing similar logic to Trade Model Lines"""
  # Constants and variables shared by tests
  base_unit_quantity = 0.01

  # Helpers
  def createResource(self, portal_type, **kw):
    module = self.portal.getDefaultModule(portal_type=portal_type)
    return module.newContent(portal_type=portal_type, **kw)

  # Steps
  def stepCreatePriceCurrency(self, sequence=None, **kw):
    sequence.edit(price_currency = self.createResource('Currency', \
        title='Currency', base_unit_quantity=self.base_unit_quantity))

  def stepCreateBusinessProcess(self, sequence=None, **kw):
    sequence.edit(business_process=self.createBusinessProcess(
      title=self.id()))

  def stepCreateBusinessLink(self, sequence=None, **kw):
    business_process = sequence.get('business_process')
    sequence.edit(business_link=self.createBusinessLink(business_process))

class TestTradeModelLine(TestTradeModelLineMixin):
  quiet = True

  # Constants and variables shared by tests
  default_discount_ratio = -0.05 # -5%
  default_tax_ratio = 0.196 # 19,6%

  new_discount_ratio = -0.04 # -4%
  new_tax_ratio = 0.22 # 22%

  node_portal_type = 'Organisation'
  order_date = DateTime()

  modified_order_line_price_ratio = 2.0
  modified_invoice_line_quantity_ratio = modified_order_line_quantity_ratio \
      = 2.5

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
              CreateBusinessLink
              ModifyBusinessLinkTaxing
              CreateBusinessLink
              ModifyBusinessLinkDiscounting
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

  # reset some values
  def afterSetUp(self):
    TestTradeModelLineMixin.afterSetUp(self)
    self.modified_packing_list_line_quantity_ratio = 0.5
    custom = self.portal.portal_skins.custom
    if custom.hasObject('TradeModelLine_getAmountProperty'):
      custom._delObject('TradeModelLine_getAmountProperty')

  # Helper methods
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

  def createOrder(self):
    module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    return module.newContent(portal_type=self.order_portal_type,
        title=self.id())

  def getTradeModelSimulationMovementList(self, order_line):
    result_list = []
    for line_simulation_movement in order_line.getOrderRelatedValueList(
        portal_type='Simulation Movement'):
      invoicing_applied_rule = [x for x in
          line_simulation_movement.objectValues()
          if x.getSpecialiseValue().getPortalType() == 'Invoice Simulation Rule'][0]
      invoicing_movement = invoicing_applied_rule.objectValues()[0]
      trade_model_rule = [x for x in invoicing_movement.objectValues()
          if x.getSpecialiseValue().getPortalType() == 'Trade Model Simulation Rule'][0]
      result_list.append(trade_model_rule.objectValues())
    return result_list

  def checkInvoiceTransactionRule(self, trade_model_simulation_movement):
    invoice_transaction_rule_list = trade_model_simulation_movement\
        .objectValues()
    self.assertEquals(1, len(invoice_transaction_rule_list))
    invoice_transaction_rule = invoice_transaction_rule_list[0]
    self.assertEqual('Invoice Transaction Simulation Rule',
        invoice_transaction_rule.getSpecialiseValue().getPortalType())

    invoice_transaction_simulation_movement_list = invoice_transaction_rule \
        .objectValues()

    self.assertEqual(2, len(invoice_transaction_simulation_movement_list))

    for movement in invoice_transaction_simulation_movement_list:
      self.assertEqual(abs(movement.getQuantity()),
          abs(trade_model_simulation_movement.getTotalPrice()))

  def createTradeCondition(self):
    module = self.portal.getDefaultModule(
        portal_type=self.trade_condition_portal_type)
    trade_condition = module.newContent(
        portal_type=self.trade_condition_portal_type,
        title=self.id())
    return trade_condition

  def createTradeModelLine(self, document, **kw):
    return document.newContent(
        portal_type='Trade Model Line',
        **kw)

  def stepModifyBusinessLinkDiscounting(self, sequence=None, **kw):
    category_tool = self.getCategoryTool()
    predecessor = category_tool.trade_state.invoiced
    successor = category_tool.trade_state.taxed
    business_link = sequence.get('business_link')
    self.assertNotEqual(None, predecessor)
    self.assertNotEqual(None, successor)

    business_link.edit(
      predecessor_value = predecessor,
      successor_value = successor,
      trade_phase = 'default/discount'
    )
    sequence.edit(business_link=None, business_link_discounting=business_link)

  def stepModifyBusinessLinkTaxing(self, sequence=None, **kw):
    category_tool = self.getCategoryTool()
    predecessor = category_tool.trade_state.invoiced
    successor = category_tool.trade_state.taxed
    business_link = sequence.get('business_link')
    self.assertNotEqual(None, predecessor)
    self.assertNotEqual(None, successor)

    business_link.edit(
      predecessor_value = predecessor,
      successor_value = successor,
      trade_phase = 'default/tax'
    )
    sequence.edit(business_link=None, business_link_taxing=business_link)

  def stepAcceptDecisionQuantityInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    solver_tool = self.portal.portal_solvers
    solver_process = solver_tool.newSolverProcess(invoice)
    for quantity_solver_decision in filter(
      lambda x:x.getCausalityValue().getTestedProperty()=='quantity',
      solver_process.contentValues()):
      # use Trade Model Solver.
      quantity_solver_decision.setSolverValue(self.portal.portal_types['Trade Model Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def stepAdoptPrevisionQuantityInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'quantity', 'adopt')

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

    # here, the net total price of the invoice is all invoices lines that does
    # not use a tax or a discount as resource.
    rounded_total_price = round(sum(
      [movement.getTotalPrice() for movement in invoice.getMovementList()
        if movement.getResource() not in (invoice_line_tax.getResource(),
                                   invoice_line_discount.getResource())]),
        currency_precision)

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

  def stepCheckOrderTaxNoSimulation(self, sequence=None, **kw):
    order_line_taxed = sequence.get('order_line_taxed')
    for trade_model_simulation_movement_list in \
        self.getTradeModelSimulationMovementList(order_line_taxed):
      self.assertEquals(0, len(trade_model_simulation_movement_list))

  # XXX: Merge: stepCheckOrderLineDiscountedSimulation stepCheckOrderLineTaxedSimulation stepCheckOrderLineDiscountedTaxedSimulation

  def stepCheckOrderLineDiscountedTaxedSimulation(self, sequence=None, **kw):
    order_line = sequence.get('order_line_discounted_taxed')
    business_link_discounting = sequence.get('business_link_discounting')
    business_link_taxing = sequence.get('business_link_taxing')
    price_currency = sequence.get('price_currency')

    service_tax = sequence.get('service_tax')
    service_discount = sequence.get('service_discount')

    self.assertNotEqual(None, business_link_discounting)
    self.assertNotEqual(None, business_link_taxing)
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
        business_link_discounting,
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
        business_link_taxing,
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
    business_link_discounting = sequence.get('business_link_discounting')
    business_link_taxing = sequence.get('business_link_taxing')
    price_currency = sequence.get('price_currency')

    service_tax = sequence.get('service_tax')
    service_discount = sequence.get('service_discount')

    self.assertNotEqual(None, business_link_discounting)
    self.assertNotEqual(None, business_link_taxing)
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
        business_link_discounting,
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
        business_link_taxing,
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
    business_link = sequence.get('business_link_taxing')
    price_currency = sequence.get('price_currency')
    self.assertNotEqual(None, business_link)
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
        business_link,
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
      int_index=10,
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
      int_index=10,
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
      int_index=30,
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
      int_index=10,
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
      int_index=20,
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
      int_index=20,
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
      int_index=20,
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
      int_index=10,
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
      int_index=10,
    )
    sequence.edit(
      trade_model_line = None,
      trade_model_line_tax = trade_model_line
    )

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

    #self.assertEqual(tax_amount.getReference(),
    #    trade_model_line_tax.getReference())
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

    #self.assertEqual(tax_amount.getReference(),
    #    trade_model_line_tax.getReference())
    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())
    self.assertSameSet([], tax_amount.getBaseContributionList())

    #self.assertEqual(discount_amount.getReference(),
    #    trade_model_line_discount.getReference())
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

    #self.assertEqual(discount_amount.getReference(),
    #    trade_model_line_discount.getReference())
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

    #self.assertEqual(discount_amount.getReference(),
    #    trade_model_line_discount.getReference())
    self.assertSameSet(['base_amount/discount'], discount_amount. \
        getBaseApplicationList())

    self.assertSameSet(['base_amount/tax'], discount_amount. \
        getBaseContributionList())

    self.assertSameSet(['base_amount/tax'], tax_amount. \
        getBaseApplicationList())

    self.assertSameSet([], tax_amount.getBaseContributionList())
    #self.assertEqual(tax_amount.getReference(),
    #    trade_model_line_tax.getReference())

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

  def assertSameUidSet(self, a, b, msg=None):
    self.assertEqual(set(x.uid for x in a), set(x.uid for x in b), msg)

  # Tests
  def test_TradeConditionCircularCompositionIsSafe(self):
    order = self.createOrder()
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    order.setSpecialiseValue(trade_condition_1)
    trade_condition_1.setSpecialiseValue(trade_condition_2)
    trade_condition_2.setSpecialiseValue(trade_condition_1)

    self.assertEqual(trade_condition_1.findEffectiveSpecialiseValueList(order),
        [trade_condition_1, trade_condition_2]
    )

  def test_findEffectiveSpecialiseValueListWithPortalType(self):
    '''
      check that findSpecialiseValueList is able to return all the inheritance
      model tree using Depth-first search with a specific portal_type asked

                                  trade_condition_1
                                    /           \
                                   /             \
                                  /               \
                       trade_condition_2       trade_condition_3
                               |
                               |
                               |
                        trade_condition_4
                               |
                               |
                               |
                        business_process
                        
    As only business_process will be a "Business Process" and we search for business process
    the result must be [business_process]
    '''
    order = self.createOrder()
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()
    trade_condition_3 = self.createTradeCondition()
    trade_condition_4 = self.createTradeCondition()
    business_process = self.createBusinessProcess()

    order.setSpecialiseValue(trade_condition_1)
    trade_condition_1.setSpecialiseValueList((trade_condition_2,
      trade_condition_3))
    trade_condition_2.setSpecialiseValue(trade_condition_4)
    trade_condition_4.setSpecialiseValue(business_process)

    self.assertEqual(trade_condition_1.findEffectiveSpecialiseValueList(order),
      [trade_condition_1, trade_condition_2, trade_condition_3,
       trade_condition_4])
    self.assertEqual(trade_condition_1.findEffectiveSpecialiseValueList(order,
      portal_type_list = ['Business Process']), [business_process])

  def test_tradeModelLineWithFixedPrice(self):
    """
      Check it's possible to have fixed quantity on lines. Sometimes we want
      to say "discount 10 euros" or "pay more 10 euros" instead of saying "10%
      discount from total"
    """
    trade_condition = self.createTradeCondition()
    tax = self.createResource('Service', title='Tax', use='tax')
    # create a model line with 100 euros
    A = self.createTradeModelLine(trade_condition, reference='A',
                                  resource_value=tax, quantity=100, price=1)
    # add a discount of 10 euros
    B = self.createTradeModelLine(trade_condition, reference='B',
                                  resource_value=tax, quantity=10, price=-1)
    order = self.createOrder()
    order.setSpecialiseValue(trade_condition)
    amount_list = order.getGeneratedAmountList()
    self.assertEqual([-10, 100], sorted(x.getTotalPrice() for x in amount_list))

  def test_getAggregatedAmountList(self, quiet=quiet):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines
    """
    sequence_list = SequenceList()
    sequence_string = self.AGGREGATED_AMOUNT_LIST_COMMON_SEQUENCE_STRING

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING = \
      COMMON_DOCUMENTS_CREATION_SEQUENCE_STRING + """
              CreateBusinessProcess
              CreateBusinessLink
              ModifyBusinessLinkTaxing
              CreateBusinessLink
              ModifyBusinessLinkDiscounting
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

  def test_getAggregatedAmountListOrderSpecialise(self, quiet=quiet):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines and order itself defines Trade Model Line
    """
    sequence_list = SequenceList()
    sequence_string = self\
        .ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

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

  def test_TradeModelRuleSimulationExpand(self, quiet=quiet):
    """Tests tree of simulations from Trade Model Rule"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationReexpand(self, quiet=quiet):
    """Tests tree of simulations from Trade Model Rule with reexpanding"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING + """
              ModifyAgainOrderLineTaxed
              ModifyAgainOrderLineDiscounted
              ModifyAgainOrderLineDiscountedTaxed
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationReexpandResourceChange(self, quiet=quiet):
    """Tests tree of simulations from Trade Model Rule with reexpanding when resource changes on model"""
    sequence_list = SequenceList()
    sequence_string = self.TRADE_MODEL_RULE_SIMULATION_SEQUENCE_STRING + """
              CreateServiceTax
              CreateServiceDiscount
              OrderCreateTradeModelLine
              ModifyTradeModelLineDiscount
              OrderCreateTradeModelLine
              ModifyTradeModelLineTax
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING = \
      ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING + """
              Tic
              PlanOrder
              Tic
  """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING

  def test_TradeModelRuleSimulationExpandOrderSpecialise(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence_string = self \
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationReexpandOrderSpecialise(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence_string = self \
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING+ """
              ModifyAgainOrderLineTaxed
              ModifyAgainOrderLineDiscounted
              ModifyAgainOrderLineDiscountedTaxed
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationWithoutBPM(self, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationWithoutTradeCondition(self, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationBuildInvoice(self, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationBuildInvoiceOrderSpecialise(self, quiet=quiet):
    sequence_list = SequenceList()
    sequence_string = self\
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING
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
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationBuildInvoiceNewTradeCondition(self, quiet=quiet):
    """Check that after changing trade condition invoice is diverged"""
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
              CheckInvoiceCausalityStateDiverged
    """
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationBuildInvoiceNewInvoiceLineSupport(self, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationBuildInvoiceInvoiceLineModifyDivergencyAndSolving(self, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationBuildInvoiceBuildInvoiceTransactionLines(self, quiet=quiet):
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
    sequence_list.play(self, quiet=quiet)

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

  def test_TradeModelRuleSimulationPackingListSplitBuildInvoiceBuildDifferentRatio(self, quiet=quiet):
    """Check building invoice after splitting packing list using different ratio"""
    self.modified_packing_list_line_quantity_ratio = 0.4
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
        self.PACKING_LIST_SPLIT_INVOICE_BUILD_SEQUENCE_STRING)
    sequence_list.play(self, quiet=quiet)

  def test_TradeModelRuleSimulationPackingListSplitBuildInvoiceBuild(self, quiet=quiet):
    """Check building invoice after splitting packing list"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
        self.PACKING_LIST_SPLIT_INVOICE_BUILD_SEQUENCE_STRING)
    sequence_list.play(self, quiet=quiet)

  def test_getAggregatedAmountListWithComplexModelLinesCreateInEasyOrder(self, quiet=quiet):
    """
    Test the return of getAggregatedAmountList in the case of many model lines
    depending each others. In this test, lines are created in the order of the
    dependencies (it means that if a line A depend of a line B, line B is
    created before A). This is the most easy case.

    Dependency tree :
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
              CreateBusinessLink
              ModifyBusinessLinkTaxing
              CreateBusinessLink
              ModifyBusinessLinkDiscounting
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
    sequence_list.play(self, quiet=quiet)

  def test_getAggregatedAmountListWithComplexModelLinesCreateInRandomOrder(self, quiet=quiet):
    """
    Test the return of getAggregatedAmountList in the case of many model lines
    depending each others. In this test, lines are created in a random order,
    not in the dependencies order (it means that if a line A depend of a 
    line B, line A can be created before line B). getAggregatedAmountList
    should be able to handle this case and redo calculation until all
    dependencies are satisfied

    Dependency tree :
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
              CreateBusinessLink
              ModifyBusinessLinkTaxing
              CreateBusinessLink
              ModifyBusinessLinkDiscounting
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
    sequence_list.play(self, quiet=quiet)

  def test_BuildTradeModelLineAndAccountingFromOrder(self):
    business_process = self.createBusinessProcess()
    business_link = self.createBusinessLink(business_process,
                              trade_phase='default/tax')

    product = self.createResource('Product',
                              title='Product',
                              use='normal',
                              base_contribution='base_amount/tax')
    tax = self.createResource('Service',
                              title='Tax',
                              use='tax')
    currency = self.createResource('Currency', title='EUR')
    trade_condition = self.createTradeCondition()
    trade_condition.setSpecialiseValue(business_process)
    trade_model_line = self.createTradeModelLine(
                              trade_condition,
                              reference='VAT',
                              price=.15,
                              resource_value=tax,
                              trade_phase='default/tax',
                              base_application='base_amount/tax',)
    source = self.portal.organisation_module.newContent(
                              portal_type='Organisation')
    destination = self.portal.organisation_module.newContent(
                              portal_type='Organisation')

    order = self.createOrder()
    order.edit(source_value=source,
               destination_value=destination,
               source_section_value=source,
               destination_section_value=destination,
               specialise_value=trade_condition,
               price_currency_value=currency,
               start_date=self.order_date,
               stop_date=self.order_date,)
    order.newContent(
                portal_type=self.order_line_portal_type,
                resource_value=product,
                quantity=10,
                price=100)

    order.plan()
    order.confirm()
    transaction.commit()
    self.tic()

    packing_list = order.getCausalityRelatedValue(
                      portal_type=self.packing_list_portal_type)
    self.assertNotEquals(packing_list, None)
    self.assertEquals(1000, packing_list.getTotalPrice())
    
    packing_list.start()
    packing_list.stop()
    packing_list.deliver()

    transaction.commit()
    self.tic()

    invoice = packing_list.getCausalityRelatedValue(
                      portal_type=self.invoice_portal_type)
    self.assertNotEquals(invoice, None)
    self.assertEquals(2, len(invoice.getMovementList()))
    self.assertEquals(1150, invoice.getTotalPrice())
    self.assertEquals([], invoice.getDivergenceList())
    
    invoice.start()
    transaction.commit()
    self.tic()

    self.assertEquals([], invoice.getDivergenceList())
    accounting_line_list = invoice.getMovementList(
             portal_type=self.invoice_transaction_line_portal_type)
    self.assertEquals(3, len(accounting_line_list))

    receivable_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.receivable_account]
    self.assertEquals(1, len(receivable_movement_list))
    receivable_movement = receivable_movement_list[0]
    self.assertEquals(receivable_movement.getDestinationValue(),
                      self.payable_account)
    self.assertEquals(1150, receivable_movement.getSourceDebit())

    collected_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.collected_tax_account]
    self.assertEquals(1, len(collected_movement_list))
    collected_movement = collected_movement_list[0]
    self.assertEquals(collected_movement.getDestinationValue(),
                      self.refundable_tax_account)
    self.assertEquals(150, collected_movement.getSourceCredit())

    income_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.income_account]
    self.assertEquals(1, len(income_movement_list))
    income_movement = income_movement_list[0]
    self.assertEquals(income_movement.getDestinationValue(),
                      self.expense_account)
    self.assertEquals(1000, income_movement.getSourceCredit())


  def test_BuildTradeModelLineAndAccountingFromInvoice(self):
    business_process = self.createBusinessProcess()
    business_link = self.createBusinessLink(business_process,
                              trade_phase='default/tax')

    product = self.createResource('Product',
                              title='Product',
                              use='normal',
                              base_contribution='base_amount/tax')
    tax = self.createResource('Service',
                              title='Tax',
                              use='tax')
    currency = self.createResource('Currency', title='EUR')
    trade_condition = self.createTradeCondition()
    trade_condition.setSpecialiseValue(business_process)
    trade_model_line = self.createTradeModelLine(
                              trade_condition,
                              reference='VAT',
                              price=.15,
                              resource_value=tax,
                              trade_phase='default/tax',
                              base_application='base_amount/tax',)
    source = self.portal.organisation_module.newContent(
                              portal_type='Organisation')
    destination = self.portal.organisation_module.newContent(
                              portal_type='Organisation')

    invoice = self.portal.accounting_module.newContent(
               portal_type=self.invoice_portal_type,
               source_value=source,
               destination_value=destination,
               source_section_value=source,
               destination_section_value=destination,
               specialise_value=trade_condition,
               price_currency_value=currency,
               start_date=self.order_date,
               stop_date=self.order_date,
               created_by_builder=True)
    invoice.newContent(
                portal_type=self.invoice_line_portal_type,
                resource_value=product,
                quantity=10,
                price=100)

    invoice.plan()
    invoice.confirm()
    transaction.commit()
    self.tic()

    self.assertEquals(2, len(invoice.getMovementList()))
    self.assertEquals(1150, invoice.getTotalPrice())
    self.assertEquals([], invoice.getDivergenceList())

    invoice.start()
    transaction.commit()
    self.tic()

    self.assertEquals([], invoice.getDivergenceList())
    accounting_line_list = invoice.getMovementList(
             portal_type=self.invoice_transaction_line_portal_type)
    self.assertEquals(3, len(accounting_line_list))

    receivable_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.receivable_account]
    self.assertEquals(1, len(receivable_movement_list))
    receivable_movement = receivable_movement_list[0]
    self.assertEquals(receivable_movement.getDestinationValue(),
                      self.payable_account)
    self.assertEquals(1150, receivable_movement.getSourceDebit())

    collected_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.collected_tax_account]
    self.assertEquals(1, len(collected_movement_list))
    collected_movement = collected_movement_list[0]
    self.assertEquals(collected_movement.getDestinationValue(),
                      self.refundable_tax_account)
    self.assertEquals(150, collected_movement.getSourceCredit())

    income_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.income_account]
    self.assertEquals(1, len(income_movement_list))
    income_movement = income_movement_list[0]
    self.assertEquals(income_movement.getDestinationValue(),
                      self.expense_account)
    self.assertEquals(1000, income_movement.getSourceCredit())

  def test_tradeModelLineWithTargetLevelSetting(self):
    """
      Test that target level setting can specify a target of trade model line
      and trade model line can works with appropriate context(delivery or
      movement) only.
    """
    tax = self.createResource('Service', title='Tax', use='tax')
    trade_condition = self.createTradeCondition()
    # create a model line and set target level to `delivery`.
    # XXX When it is possible to accumulate contributed quantities between
    #     input amounts, the trade condition should be configured as follows:
    # tml1: - price=1, no resource
    #       - base_application='base_amount/tax'
    #       - base_contribution='base_amount/some_accumulating_category'
    # tml2: - price=0.05, resource=tax
    #       - base_application='base_amount/some_accumulating_category'
    #       - test_method_id='isDelivery'
    # And remove 'base_amount/tax' from base_contribution_list on order.
    tml = self.createTradeModelLine(trade_condition,
                                    reference='TAX',
                                    resource_value=tax,
                                    base_application='base_amount/tax',
                                    test_method_id='isDelivery',
                                    price=0.05)

    # create an order.
    resource_A = self.createResource('Product', title='A')
    resource_B = self.createResource('Product', title='B')
    order = self.createOrder()
    order.setSpecialiseValue(trade_condition)
    base_contribution_list = 'base_amount/tax', 'base_amount/extra_fee'
    order.setBaseContributionList(base_contribution_list)
    kw = {'portal_type': self.order_line_portal_type,
          'base_contribution_list': base_contribution_list}
    order_line_1 = order.newContent(price=1000, quantity=1,
                                    resource_value=resource_A, **kw)
    order_line_2 = order.newContent(price=500, quantity=1,
                                    resource_value=resource_B, **kw)
    amount_list = order.getGeneratedAmountList()
    self.assertEqual([75], [x.getTotalPrice() for x in amount_list])

    # change target level to `movement`.
    tml.setTestMethodId('isMovement')
    amount_list = order.getGeneratedAmountList()
    self.assertEqual([25, 50], sorted(x.getTotalPrice() for x in amount_list))

    # create other trade model lines.
    # for movement
    extra_fee_a = self.createTradeModelLine(trade_condition,
                                            reference='EXTRA_FEE_A',
                                            resource_value=tax,
                                            base_application='base_amount/extra_fee',
                                            test_method_id='isMovement',
                                            price=.2)
    # Use custom script to return a movement which has a fixed value of quantity.
    # If a fixed quantity value is set to trade model line directly then it is
    # applied to all the movements without matching base_application category.
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_getAmountProperty',
      'amount, base_application, *args, **kw',
      """\
if base_application == 'base_amount/extra_fee':
  return min(800, amount.getTotalPrice())
""")
    # Extra fee b has a fixed quantity so that this trade model line is applied
    # to all movements by force.
    extra_fee_b = self.createTradeModelLine(trade_condition,
                                            reference='EXTRA_FEE_B',
                                            resource_value=tax,
                                            test_method_id='isMovement',
                                            price=1)
    # for delivery level
    discount = self.createTradeModelLine(trade_condition,
                                         reference='DISCOUNT_B',
                                         resource_value=tax,
                                         test_method_id='isDelivery',
                                         quantity=10, price=-1)

    transaction.commit() # flush transactional cache

    expected_tax = 1000*0.05, 500*0.05, 500*0.2, 800*0.2, 1, 1, -10
    amount_list = order.getGeneratedAmountList()
    self.assertEqual(sorted(expected_tax),
                     sorted(x.getTotalPrice() for x in amount_list))
    amount_list = order.getAggregatedAmountList()
    expected_tax = 1000*0.05 + 500*0.05, 500*0.2 + 800*0.2, 1 + 1, -10
    self.assertEqual(sorted(expected_tax),
                     sorted(x.getTotalPrice() for x in amount_list))

    # Change target level
    extra_fee_a.setTestMethodId('isDelivery')
    extra_fee_b.setTestMethodId('isDelivery')
    amount_list = order.getAggregatedAmountList()
    expected_tax = 1000*0.05 + 500*0.05, 800*0.2, 1, -10
    self.assertEqual(sorted(expected_tax),
                     sorted(x.getTotalPrice() for x in amount_list))

  @expectedFailure
  def test_tradeModelLineWithRounding(self):
    """
      Test if trade model line works with rounding.
    """
    trade_condition = self.createTradeCondition()
    # create a model line and set target level to `delivery`
    tax = self.createTradeModelLine(trade_condition,
                                    reference='TAX',
                                    base_application_list=['base_amount/tax'],
                                    base_contribution_list=['base_amount/total_tax'])
    tax.edit(price=0.05, target_level=TARGET_LEVEL_DELIVERY)

    # create a rounding model for tax
    rounding_model = self.portal.portal_roundings.newContent(portal_type='Rounding Model')
    rounding_model.setDecimalRoundingOption('ROUND_DOWN')
    rounding_model.setDecimalExponent('1')
    rounding_model.setRoundedPropertyId('total_price')
    rounding_model._setMembershipCriterionCategoryList(['base_contribution/base_amount/total_tax'])
    rounding_model._setMembershipCriterionBaseCategoryList(['base_contribution'])
    rounding_model.validate()

    # create an order
    resource_A = self.createResource('Product', title='A')
    resource_B = self.createResource('Product', title='B')
    order = self.createOrder()
    order.setSpecialiseValue(trade_condition)
    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    price=3333, quantity=1,
                                    resource_value=resource_A,
                                    base_contribution_list=['base_amount/tax'])
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    price=171, quantity=1,
                                    resource_value=resource_B,
                                    base_contribution_list=['base_amount/tax'])

    transaction.commit()
    self.tic()

    # check the result without rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=False)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(set([order_line_1, order_line_2]),
                     set(amount_list[0].getCausalityValueList()))
    self.assertEqual((3333+171)*0.05, amount_list[0].getTotalPrice())
    # check the result with rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=True)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(set([order_line_1, order_line_2]),
                     set(amount_list[0].getCausalityValueList()))
    self.assertEqual(175, amount_list[0].getTotalPrice())

    # change tax trade model line to `movement` level
    tax.edit(target_level=TARGET_LEVEL_MOVEMENT)

    def getTotalAmount(amount_list):
      result = 0
      for amount in amount_list:
        if amount.getBaseContribution() in ('base_amount/total', 'base_amount/total_tax'):
          result += amount.getTotalPrice()
      return result

    # check the result without rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=False)
    self.assertEqual(2, len(amount_list))
    self.assertEqual(3333*0.05+171*0.05, getTotalAmount(amount_list))
    # check the result with rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=True)
    self.assertEqual(2, len(amount_list))
    self.assertEqual(174, getTotalAmount(amount_list))

    # check getAggregatedAmountList result of each movement
    # order line 1
    amount_list = trade_condition.getAggregatedAmountList(order_line_1,
                                                          rounding=False)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(3333*0.05, amount_list[0].getTotalPrice())
    amount_list = trade_condition.getAggregatedAmountList(order_line_1,
                                                          rounding=True)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(166, amount_list[0].getTotalPrice())
    # order line 2
    amount_list = trade_condition.getAggregatedAmountList(order_line_2,
                                                          rounding=False)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(171*0.05, amount_list[0].getTotalPrice())
    amount_list = trade_condition.getAggregatedAmountList(order_line_2,
                                                          rounding=True)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(8, amount_list[0].getTotalPrice())

    # change rounding model definition
    rounding_model.setDecimalRoundingOption('ROUND_UP')
    rounding_model.setDecimalExponent('1')
    rounding_model.setRoundedPropertyIdList(['total_price', 'quantity'])

    # change quantity
    order_line_1.edit(quantity=3.3333)

    transaction.commit()
    self.tic()

    # check the result without rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=False)
    self.assertEqual(2, len(amount_list))
    self.assertEqual(3.3333*3333*0.05+171*0.05, getTotalAmount(amount_list))
    # check the result with rounding
    # both quantity and total price will be rounded so that the expression
    # should be "round_up(round_up(3.3333 * 3333) * 0.05) + round_up(round_up
    # (1* 171) * 0.05)"
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=True)
    self.assertEqual(2, len(amount_list))
    self.assertEqual(565, getTotalAmount(amount_list))

    # create a rounding model to round quantity property of order line
    rounding_model_for_quantity = self.portal.portal_roundings.newContent(portal_type='Rounding Model')
    rounding_model_for_quantity.setDecimalRoundingOption('ROUND_DOWN')
    rounding_model_for_quantity.setDecimalExponent('1')
    rounding_model_for_quantity.setRoundedPropertyId('quantity')
    rounding_model_for_quantity._setMembershipCriterionCategoryList(['base_contribution/base_amount/tax'])
    rounding_model_for_quantity._setMembershipCriterionBaseCategoryList(['base_contribution'])
    rounding_model_for_quantity.validate()

    transaction.commit()
    self.tic()

    amount_list = trade_condition.getAggregatedAmountList(order, rounding=True)
    # The expression should be "round_up(round_up(round_down(3.3333) * 3333)
    # * 0.05) + round_up(round_up(round_down(1) * 171) * 0.05)"
    self.assertEqual(2, len(amount_list))
    self.assertEqual(509, getTotalAmount(amount_list))

    # create a rounding model to round price property of order line
    rounding_model_for_price = self.portal.portal_roundings.newContent(portal_type='Rounding Model')
    rounding_model_for_price.setDecimalRoundingOption('ROUND_UP')
    rounding_model_for_price.setDecimalExponent('0.1')
    rounding_model_for_price.setRoundedPropertyId('price')
    rounding_model_for_price._setMembershipCriterionCategoryList(['base_contribution/base_amount/tax'])
    rounding_model_for_price._setMembershipCriterionBaseCategoryList(['base_contribution'])
    rounding_model_for_price.validate()

    # change price
    order_line_2.edit(price=171.1234)
    # invalidate rounding model for total price
    rounding_model.invalidate()

    transaction.commit()
    self.tic()

    # check the result without rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=False)
    self.assertEqual(2, len(amount_list))
    self.assertEqual(3.3333*3333*0.05+171.1234*0.05, getTotalAmount(amount_list))
    # check the result with rounding
    amount_list = trade_condition.getAggregatedAmountList(order, rounding=True)
    # The expression should be "round_down(3.3333) * round_up(3333) * 0.05 +
    # round_down(1) * round_up(171.1234) * 0.05"
    self.assertEqual(2, len(amount_list))
    self.assertEqual(508.51000000000005, getTotalAmount(amount_list))

class TestTradeModelLineSale(TestTradeModelLine):
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  packing_list_portal_type = 'Sale Packing List'
  trade_condition_portal_type = 'Sale Trade Condition'

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeModelLineSale))
  return suite
