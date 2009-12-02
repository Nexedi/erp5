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

from Products.ERP5.tests.testBPMCore import TestBPMMixin
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.ERP5Type.tests.utils import createZODBPythonScript
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.ERP5.PropertySheet.TradeModelLine import (TARGET_LEVEL_MOVEMENT,
                                                        TARGET_LEVEL_DELIVERY)

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

  def stepCreateBusinessPath(self, sequence=None, **kw):
    business_process = sequence.get('business_process')
    sequence.edit(business_path=self.createBusinessPath(business_process))

class TestTradeModelLine(TestTradeModelLineMixin):
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

  modified_packing_list_line_quantity_ratio = 0.5

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
          if x.getSpecialiseValue().getPortalType() == 'Invoicing Rule'][0]
      invoicing_movement = invoicing_applied_rule.objectValues()[0]
      trade_model_rule = [x for x in invoicing_movement.objectValues()
          if x.getSpecialiseValue().getPortalType() == 'Trade Model Rule'][0]
      result_list.append(trade_model_rule.objectValues())
    return result_list

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

  # Steps
  def stepCreateBusinessState(self, sequence=None, **kw):
    business_process = sequence.get('business_process')
    sequence.edit(business_state=self.createBusinessState(business_process))

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

  def stepModifyBusinessStateTaxed(self, sequence=None, **kw):
    business_state = sequence.get('business_state')
    business_state.edit(reference='taxed')
    sequence.edit( business_state=None, business_state_taxed=business_state)

  def stepModifyBusinessStateInvoiced(self, sequence=None,
                sequence_string=None):
    business_state = sequence.get('business_state')
    business_state.edit(reference='invoiced')
    sequence.edit(business_state=None, business_state_invoiced=business_state)

  def stepAcceptDecisionQuantityInvoice(self, sequence=None, **kw):
    invoice = sequence.get('invoice')
    self._solveDivergence(invoice, 'quantity', 'accept')

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

  # Tests
  def test_TradeConditionTradeModelLineBasicComposition(self):
    """
      If Trade Condition is specialised by another Trade Condition they
      Trade Model Lines shall be merged.
    """
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValue(trade_condition_2)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        reference='A')

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        reference='B')

    self.assertSameSet(
      [trade_condition_1_trade_model_line,
        trade_condition_2_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

  def test_TradeConditionTradeModelLineBasicCompositionWithOrder(self):
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()
    order = self.createOrder()

    trade_condition_1.setSpecialiseValue(trade_condition_2)
    order.setSpecialiseValue(trade_condition_1)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        reference='A')

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        reference='B')

    order_trade_model_line = self.createTradeModelLine(
        order,
        reference='C')

    self.assertSameSet(
      [trade_condition_1_trade_model_line, trade_condition_2_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

    self.assertSameSet(
      [trade_condition_1_trade_model_line, trade_condition_2_trade_model_line,
        order_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList(context=order)
    )

  def test_TradeConditionCircularCompositionIsSafe(self):
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValue(trade_condition_2)
    trade_condition_2.setSpecialiseValue(trade_condition_1)

    self.assertEquals(trade_condition_1. \
        findSpecialiseValueList(trade_condition_1),
        [trade_condition_1, trade_condition_2]
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

      According to Depth-first search algorithm, result of this graph is:
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

    speciliase_value_list = trade_condition_1.findSpecialiseValueList(
        context=trade_condition_1)
    self.assertEquals(len(speciliase_value_list), 4)
    self.assertEquals(
      [trade_condition_1, trade_condition_2, trade_condition_3,
       trade_condition_4], speciliase_value_list)

  def test_TradeConditionTradeModelLineReferenceIsShadowingComposition(self):
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()

    trade_condition_1.setSpecialiseValue(trade_condition_2)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        reference='A')

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        reference='A')

    self.assertSameSet(
      [trade_condition_1_trade_model_line],
      trade_condition_1.getTradeModelLineComposedList()
    )

  def test_TradeConditionTradeModelLineReferenceIsShadowingCompositionWithOrder(self):
    trade_condition_1 = self.createTradeCondition()
    trade_condition_2 = self.createTradeCondition()
    order = self.createOrder()

    trade_condition_1.setSpecialiseValue(trade_condition_2)
    order.setSpecialiseValue(trade_condition_1)

    trade_condition_1_trade_model_line = self.createTradeModelLine(
        trade_condition_1,
        reference = 'A')

    trade_condition_2_trade_model_line = self.createTradeModelLine(
        trade_condition_2,
        reference = 'B')

    order_trade_model_line = self.createTradeModelLine(
        order,
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
        or
      * (DEFG) (BC) A
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
    self.assertEquals([q.getReference() for q in trade_model_line_list],
        [q.getReference() for q in [G, F, E, D, C, B, A]])

  def test_getComplexTradeModelLineComposedList(self):
    """Test that list of contribution/application relations is sorted to do easy traversal

    Let assume such graph of contribution/application dependency:

             /--------\
            /          \
      A----+ -----B-----+-D
            \          /
             \----C---/

    It shall return list which is sorted like:
      * A (BC) D
    where everything in parenthesis can be not sorted
    """
    trade_condition = self.createTradeCondition()

    C = self.createTradeModelLine(trade_condition, reference='C',
        base_contribution_list=['base_amount/total'],
        base_application_list=['base_amount/total_discount'])

    A = self.createTradeModelLine(trade_condition, reference='A',
        base_contribution_list=['base_amount/total', 'base_amount/total_tax',
          'base_amount/total_discount'],
        base_application_list=['base_amount/tax'])

    D = self.createTradeModelLine(trade_condition, reference='D',
        base_application_list=['base_amount/total'])

    B = self.createTradeModelLine(trade_condition, reference='B',
        base_contribution_list=['base_amount/total'],
        base_application_list=['base_amount/total_tax'])

    trade_model_line_list = trade_condition.getTradeModelLineComposedList()

    # XXX: This is only one good possible sorting
    self.assertEquals([q.getReference() for q in trade_model_line_list],
        [q.getReference() for q in [A, B, C, D]])

  def test_tradeModelLineWithFixedPrice(self):
    """
      Check it's possible to have fixed quantity on lines. Sometimes we want
      to say "discount 10 euros" or "pay more 10 euros" instead of saying "10%
      discount from total"
    """
    trade_condition = self.createTradeCondition()

    # create a model line with 100 euros
    A = self.createTradeModelLine(trade_condition, reference='A',
        base_contribution_list=['base_amount/total'])
    A.edit(quantity=100, price=1)

    # add a discount of 10 euros
    B = self.createTradeModelLine(trade_condition, reference='B',
        base_contribution_list=['base_amount/total'])
    B.edit(quantity=10, price=-1)

    order = self.createOrder()
    order.setSpecialiseValue(trade_condition)
    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEquals(2, len(amount_list))
    total_amount_list = [q for q in amount_list
        if q.getBaseContribution() == 'base_amount/total']

    self.assertEquals(2, len(total_amount_list))

    # the total amount for base_amount/total should be of 100 - 10 = 90 euros
    total_amount = 0
    for amount in total_amount_list:
      total_amount += amount.getTotalPrice()

    self.assertEqual(total_amount, 100 - 10)

  def test_getAggregatedAmountList(self):
    """
      Test for case, when discount contributes to tax, and order has mix of contributing lines
    """
    sequence_list = SequenceList()
    sequence_string = self.AGGREGATED_AMOUNT_LIST_COMMON_SEQUENCE_STRING

    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

  def test_TradeModelRuleSimulationReexpandResourceChange(self):
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
    sequence_list.play(self, quiet=True)

  TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING = \
      ORDER_SPECIALISE_AGGREGATED_AMOUNT_COMMON_SEQUENCE_STRING + """
              Tic
              PlanOrder
              Tic
  """ + AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING

  def test_TradeModelRuleSimulationExpandOrderSpecialise(self):
    sequence_list = SequenceList()
    sequence_string = self \
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=True)

  def test_TradeModelRuleSimulationReexpandOrderSpecialise(self):
    sequence_list = SequenceList()
    sequence_string = self \
        .TRADE_MODEL_RULE_SIMULATION_ORDER_SPECIALISED_SEQUENCE_STRING+ """
              ModifyAgainOrderLineTaxed
              ModifyAgainOrderLineDiscounted
              ModifyAgainOrderLineDiscountedTaxed
              Tic
    """ + self.AGGREGATED_AMOUNT_SIMULATION_CHECK_SEQUENCE_STRING
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

  def test_TradeModelRuleSimulationBuildInvoice(self):
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
    sequence_list.play(self, quiet=True)

  def test_TradeModelRuleSimulationBuildInvoiceOrderSpecialise(self):
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
    sequence_list.play(self, quiet=True)

  def test_TradeModelRuleSimulationBuildInvoiceNewTradeCondition(self):
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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

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
    sequence_list.play(self, quiet=True)

  def test_TradeModelRuleSimulationPackingListSplitBuildInvoiceBuild(self):
    """Check building invoice after splitting packing list"""
    sequence_list = SequenceList()
    sequence_list.addSequenceString(
        self.PACKING_LIST_SPLIT_INVOICE_BUILD_SEQUENCE_STRING)
    sequence_list.play(self, quiet=True)

  def test_getAggregatedAmountListWithComplexModelLinesCreateInEasyOrder(self):
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
    sequence_list.play(self, quiet=True)

  def test_getAggregatedAmountListWithComplexModelLinesCreateInRandomOrder(self):
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
    sequence_list.play(self, quiet=True)

  def test_BuildTradeModelLineAndAccountingFromOrder(self):
    business_process = self.createBusinessProcess()
    business_path = self.createBusinessPath(business_process,
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
    business_path = self.createBusinessPath(business_process,
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
    trade_condition = self.createTradeCondition()
    # create a model line and set target level to `delivery`.
    tax = self.createTradeModelLine(trade_condition,
                                    reference='TAX',
                                    base_application_list=['base_amount/tax'],
                                    base_contribution_list=['base_amount/total_tax'])
    tax.edit(price=0.05, target_level=TARGET_LEVEL_DELIVERY)

    # create an order.
    resource_A = self.createResource('Product', title='A')
    resource_B = self.createResource('Product', title='B')
    order = self.createOrder()
    order.setSpecialiseValue(trade_condition)
    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    price=1000, quantity=1,
                                    resource_value=resource_A,
                                    base_contribution_list=['base_amount/tax'])
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    price=500, quantity=1,
                                    resource_value=resource_B,
                                    base_contribution_list=['base_amount/tax'])
    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEqual(1, len(amount_list))
    self.assertEqual(set([order_line_1, order_line_2]),
                     set(amount_list[0].getCausalityValueList()))
    self.assertEqual(75.0, amount_list[0].getTotalPrice())

    # change target level to `movement`.
    tax.edit(target_level=TARGET_LEVEL_MOVEMENT)
    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEqual(2, len(amount_list))
    self.assertEqual(1,
                     len([1 for amount in amount_list
                          if amount.getCausalityValueList() == [order_line_1]]))
    self.assertEqual(1,
                     len([1 for amount in amount_list
                          if amount.getCausalityValueList() == [order_line_2]]))
    # check getAggregatedAmountList result of order line.
    amount_list = trade_condition.getAggregatedAmountList(order_line_1)
    self.assertEqual(1, len(amount_list))
    self.assertEqual([order_line_1], amount_list[0].getCausalityValueList())
    amount_list = trade_condition.getAggregatedAmountList(order_line_2)
    self.assertEqual(1, len(amount_list))
    self.assertEqual([order_line_2], amount_list[0].getCausalityValueList())

    # create other trade model lines.
    # for movement
    extra_fee = self.createTradeModelLine(trade_condition,
                                          reference='EXTRA_FEE_A',
                                          base_contribution_list=['base_amount/total'])
    extra_fee.edit(quantity=100, price=1, target_level=TARGET_LEVEL_MOVEMENT)
    # for delivery level
    discount = self.createTradeModelLine(trade_condition,
                                         reference='DISCOUNT_B',
                                         base_contribution_list=['base_amount/total'],)
    discount.edit(quantity=10, price=-1, target_level=TARGET_LEVEL_DELIVERY)

    def getTotalAmount(amount_list):
      result = 0
      for amount in amount_list:
        if amount.getBaseContribution() in ('base_amount/total', 'base_amount/total_tax'):
          result += amount.getTotalPrice()
      return result

    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEqual(5, len(amount_list))
    self.assertEqual(100 + 100 - 10 + 1000*0.05 + 500*0.05,
                     getTotalAmount(amount_list))

    # Make sure that getAggregatedAmountList of movement uses movement
    # level trade model line only.
    def getMovementFromAmountListByReference(amount_list, reference):
      for amount in amount_list:
        if amount.getReference()==reference:
          return amount
    amount_list = trade_condition.getAggregatedAmountList(order_line_1)
    self.assertEqual(2, len(amount_list))
    extra_fee_a_amount = getMovementFromAmountListByReference(amount_list,
                                                              'EXTRA_FEE_A')
    self.assertEqual([],
                     extra_fee_a_amount.getCausalityValueList())
    tax_amount = getMovementFromAmountListByReference(amount_list,
                                                      'TAX')
    self.assertEqual([order_line_1],
                     tax_amount.getCausalityValueList())
    amount_list = trade_condition.getAggregatedAmountList(order_line_2)
    self.assertEqual(2, len(amount_list))
    extra_fee_a_amount = getMovementFromAmountListByReference(amount_list,
                                                              'EXTRA_FEE_A')
    self.assertEqual([],
                     extra_fee_a_amount.getCausalityValueList())
    tax_amount = getMovementFromAmountListByReference(amount_list,
                                                      'TAX')
    self.assertEqual([order_line_2],
                     tax_amount.getCausalityValueList())

    # Change target level
    extra_fee.edit(target_level=TARGET_LEVEL_DELIVERY)
    tax.edit(target_level=TARGET_LEVEL_DELIVERY)
    amount_list = trade_condition.getAggregatedAmountList(order)
    self.assertEqual(3, len(amount_list))
    self.assertEqual(100 - 10 + 1500*0.05,
                     getTotalAmount(amount_list))

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


class TestComplexTradeModelLineUseCase(TestTradeModelLineMixin):
  """This test provides several complex use cases which are seen in the normal
  shop and make sure that trade model line is capable of real business scene.
  """

  def createOrder(self):
    module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    return module.newContent(portal_type=self.order_portal_type,
        title=self.id())

  def createTradeCondition(self):
    module = self.portal.getDefaultModule(
        portal_type=self.trade_condition_portal_type)
    trade_condition = module.newContent(
        portal_type=self.trade_condition_portal_type,
        title=self.id())
    return trade_condition

  def getAmount(self, order, reference, return_object=False):
    trade_condition = order.getSpecialiseValue()
    for movement in trade_condition.getAggregatedAmountList(order):
      if movement.getReference() == reference:
        if return_object == True:
          return movement
        else:
          return movement.getTotalPrice()

  def appendBaseContributionCategory(self, document, new_category):
    base_contribution_value_list = document.getBaseContributionValueList()
    document.setBaseContributionValueList(
      base_contribution_value_list+[new_category])

  def beforeTearDown(self):
    # abort any transaction
    transaction.abort()
    # put non finished activities into ignored state
    activity_connection = self.portal.cmf_activity_sql_connection
    for table in 'message', 'message_queue':
      activity_connection.manage_test(
          'delete from %s where processing_node=-2' % table)

    def removeAll(*args):
      for container in args:
        container.manage_delObjects(ids=list(container.objectIds()))
    removeAll(self.portal.sale_order_module,
              self.portal.purchase_order_module,
              self.portal.sale_trade_condition_module,
              self.portal.purchase_trade_condition_module,
              self.portal.person_module,
              self.portal.organisation_module,
              self.portal.service_module,
              self.portal.product_module,
              self.portal.currency_module,
              self.portal.portal_categories.product_line,
              self.portal.portal_categories.base_amount,
              self.portal.portal_categories.trade_phase,
              self.portal.portal_categories.use,
              self.portal.portal_categories.quantity_unit,
              )

    self.stepTic()

  def afterSetUp(self):
    portal = self.portal

    # inherited method
    self.createCategories()

    self.stepTic()

    # add currency
    jpy = portal.currency_module.newContent(title='Yen', reference='JPY', base_unit_quantity='1')

    self.stepTic()

    # add organisations
    my_company = portal.organisation_module.newContent(title='My Company')
    client_1 = portal.organisation_module.newContent(title='Client 1')

    self.stepTic()

    # add base amount subcategories
    base_amount = portal.portal_categories.base_amount
    self.total_price_of_ordered_items = base_amount.newContent(id='total_price_of_ordered_items')
    self.discount_amount_of_non_vat_taxable = base_amount.newContent(id='discount_amount_of_non_vat_taxable')
    self.discount_amount_of_vat_taxable = base_amount.newContent(id='discount_amount_of_vat_taxable')
    self.vat_taxable = base_amount.newContent(id='vat_taxable')
    self.total_price_without_vat = base_amount.newContent(id='total_price_without_vat')
    self.total_price_of_vat_taxable = base_amount.newContent(id='total_price_of_vat_taxable')
    self.discount_amount = base_amount.newContent(id='discount_amount')
    self.vat_amount = base_amount.newContent(id='vat_amount')
    self.total_price_with_vat = base_amount.newContent(id='total_price_with_vat')
    self.poster_present_1dvd = base_amount.newContent(id='poster_present_1dvd')
    self.poster_present_3cd = base_amount.newContent(id='poster_present_3cd')
    self.special_discount_3cd = base_amount.newContent(id='special_discount_3cd')
    # add product line subcategories
    product_line = portal.portal_categories.product_line
    audio = product_line.newContent(id='audio')
    audio_cd = audio.newContent(id='cd')
    video = product_line.newContent(id='video')
    video_dvd = video.newContent(id='dvd')
    other_product = product_line.newContent(id='other')
    # add a quantity unit subcategory
    self.unit = portal.portal_categories.quantity_unit.newContent(id='unit')

    self.stepTic()

    # create services
    self.service_vat = portal.service_module.newContent(title='VAT')
    self.service_discount = portal.service_module.newContent(title='VAT')

    self.stepTic()

    # create products
    def addProductDocument(title, product_line_value):
      return portal.product_module.newContent(
        title=title,
        product_line_value=product_line_value,
        quantity_unit_value=self.unit,
        base_contribution_value_list=[self.vat_taxable,
                                      self.total_price_of_ordered_items])

    self.music_album_1 = addProductDocument('Music Album 1', audio_cd)
    self.movie_dvd_1 = addProductDocument('Movie DVD 1', video_dvd)
    self.music_album_2 = addProductDocument('Movie Album 2', audio_cd)
    self.candy = addProductDocument('Candy', other_product)
    self.poster = addProductDocument('Poster', other_product)
    self.music_album_3 = addProductDocument('Movie Album 3', audio_cd)
    self.movie_dvd_2 = addProductDocument('Movie DVD 2', video_dvd)
    self.music_album_4 = addProductDocument('Movie Album 4', audio_cd)

    self.stepTic()

    # create a trade condition and add several common trade model lines in it.
    self.trade_condition = self.createTradeCondition()
    self.trade_condition.edit(
      source_section_value=my_company,
      source_value=my_company,
      source_decision_value=my_company,
      destination_section_value=client_1,
      destination_value=client_1,
      destination_decision_value=client_1,
      price_currency_value=jpy)
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Total Price Without VAT',
      reference='TOTAL_PRICE_WITHOUT_VAT',
      price=1,
      quantity=None,
      efficiency=1,
      target_level=TARGET_LEVEL_DELIVERY,
      create_line=True,
      trade_phase=None,
      base_application_value_list=[self.discount_amount_of_non_vat_taxable,
                                   self.discount_amount_of_vat_taxable,
                                   self.total_price_of_ordered_items],
      base_contribution_value_list=[self.total_price_without_vat])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Total Price Of VAT Taxable',
      reference='TOTAL_PRICE_OF_VAT_TAXABLE',
      price=1,
      quantity=None,
      efficiency=1,
      target_level=TARGET_LEVEL_DELIVERY,
      create_line=True,
      trade_phase=None,
      base_application_value_list=[self.discount_amount_of_vat_taxable,
                                   self.vat_taxable],
      base_contribution_value_list=[self.total_price_of_vat_taxable])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Discount Amount',
      reference='DISCOUNT_AMOUNT',
      resource_value=self.service_discount,
      price=1,
      quantity=None,
      efficiency=1,
      target_level=TARGET_LEVEL_DELIVERY,
      create_line=True,
      trade_phase_value=portal.portal_categories.trade_phase.default.invoicing,
      base_application_value_list=[self.discount_amount_of_vat_taxable,
                                   self.discount_amount_of_non_vat_taxable],
      base_contribution_value_list=[self.discount_amount])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='VAT Amount',
      reference='VAT_AMOUNT',
      resource_value=self.service_vat,
      price=0.05,
      quantity=None,
      efficiency=1,
      target_level=TARGET_LEVEL_DELIVERY,
      create_line=True,
      trade_phase_value=portal.portal_categories.trade_phase.default.invoicing,
      base_application_value_list=[self.discount_amount_of_vat_taxable,
                                   self.vat_taxable],
      base_contribution_value_list=[self.vat_amount])
    self.trade_condition.newContent(
      portal_type='Trade Model Line',
      title='Total Price With VAT',
      reference='TOTAL_PRICE_WITH_VAT',
      price=1,
      quantity=None,
      efficiency=1,
      target_level=TARGET_LEVEL_DELIVERY,
      create_line=True,
      trade_phase=None,
      base_application_value_list=[self.vat_amount,
                                   self.total_price_without_vat],
      base_contribution_value_list=[self.total_price_with_vat])

    self.stepTic()

  def test_usecase1(self):
    """
    Use case 1 : Buy 3 CDs or more, get 10% off them.

    1 CD   5000 yen
    1 CD   3000 yen
    1 Candy 100 yen
    1 CD   2400 yen
    discount (5000+3000+2400) * 0.1 = 1040 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD10PercentDiscount',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      """\
total_quantity = sum([movement.getQuantity()
                      for movement in aggregated_movement_list])
if total_quantity >= 3:
  return current_movement
else:
  return None
""")
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_AND_10PERCENT_DISCOUNT_OFF_THEM',
                     resource_value=self.service_discount,
                     price=-0.1,
                     quantity=None,
                     efficiency=1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD10PercentDiscount',
                     create_line=True,
                     trade_phase=None,
                     base_application_value_list=[self.special_discount_3cd],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_1, self.special_discount_3cd)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_2, self.special_discount_3cd)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.candy,
                                    quantity=1,
                                    price=100)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 8100)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 405)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 8505)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)

    self.stepTic()

    # check again
    self.assertEqual(self.getAmount(order, '3CD_AND_10PERCENT_DISCOUNT_OFF_THEM'),
                     -1040)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 9460)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 473)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 9933)

  def test_usecase2(self):
    """
    Use case 2 : Buy 3 CDs or more, get 500 yen off.

    1 CD  5000 yen
    1 CD  3000 yen
    1 DVD 3000 yen
    1 CD  2400 yen
    discount 500 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD500YenDiscount',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      """\
total_quantity = sum([movement.getQuantity() for movement in aggregated_movement_list])
if total_quantity >= 3:
  current_movement.setQuantity(-500)
  return current_movement
else:
  return None
""")
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_AND_500YEN_OFF',
                     resource_value=self.service_discount,
                     price=1,
                     quantity=None,
                     efficiency=1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD500YenDiscount',
                     create_line=True,
                     trade_phase=None,
                     base_application_value_list=[self.special_discount_3cd],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_1, self.special_discount_3cd)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_2, self.special_discount_3cd)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 11000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 550)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 11550)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)
    # check again
    self.assertEqual(self.getAmount(order, '3CD_AND_500YEN_OFF'), -500)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 12900)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 645)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 13545)

  def test_usecase3(self):
    """
    Use case 3 : Buy 3 CDs or more, get 10% off total.

    1 CD  5000 yen
    1 DVD 3000 yen
    1 CD  3000 yen
    1 CD  2400 yen
    discount (5000+3000+3000+2400) * 0.1 = 1340 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD10PercentDiscountFromTotal',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      '''\
special_discount_3cd = context.portal_categories.base_amount.special_discount_3cd
total_quantity = sum([movement.getQuantity() for movement in current_aggregated_amount_list
                      if special_discount_3cd in movement.getBaseContributionValueList()])
if total_quantity >= 3:
  return current_movement
else:
  return None
''')
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_10PERCENT_OFF_FROM_TOTAL',
                     resource_value=self.service_discount,
                     price=-0.1,
                     quantity=None,
                     efficiency=1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD10PercentDiscountFromTotal',
                     create_line=True,
                     trade_phase=None,
                     base_application_value_list=[self.total_price_of_ordered_items],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_1, self.special_discount_3cd)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_3, self.special_discount_3cd)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 11000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 550)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 11550)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)
    # check again
    self.assertEqual(self.getAmount(order, '3CD_10PERCENT_OFF_FROM_TOTAL'),
                     -1340)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 12060)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 603)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 12663)

  def test_usecase4(self):
    """
    Use case 4 : Buy 3 CDs or 1 DVD, get 1 poster free.

    2 CD     6000 yen
    1 DVD    3000 yen
    1 Poster    0 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CDOr1DVDForPoster',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      '''\
poster_present_3cd = context.portal_categories.base_amount.poster_present_3cd
poster_present_1dvd = context.portal_categories.base_amount.poster_present_1dvd

total_quantity_3cd = sum([movement.getQuantity() for movement in aggregated_movement_list
                          if poster_present_3cd in movement.getBaseContributionValueList()])
total_quantity_1dvd = sum([movement.getQuantity() for movement in aggregated_movement_list
                           if poster_present_1dvd in movement.getBaseContributionValueList()])
if (total_quantity_3cd >= 3 or total_quantity_1dvd >= 1):
  current_movement.setQuantity(1)
  return current_movement
else:
  return None
''')
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_OR_1DVD_GET_1_POSTER_FREE',
                     resource_value=self.poster,
                     price=0,
                     quantity=None,
                     efficiency=1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CDOr1DVDForPoster',
                     create_line=True,
                     trade_phase=None,
                     base_application_value_list=[self.poster_present_1dvd,
                                                  self.poster_present_3cd])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_4,
                                    quantity=2,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_1, self.poster_present_3cd)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 6000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 300)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 6300)
    self.assertEqual(self.getAmount(order, '3CD_OR_1DVD_GET_1_POSTER_FREE'),
                     None)
    # add 1 dvd, then 1 poster will be given.
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_2, self.poster_present_1dvd)

    self.stepTic()
    
    # check again
    one_free_poster_amount = self.getAmount(order,
                                            '3CD_OR_1DVD_GET_1_POSTER_FREE',
                                            return_object=True)
    self.assertEqual(one_free_poster_amount.getTotalPrice(), 0)
    self.assertEqual(one_free_poster_amount.getQuantity(), 1)
    self.assertEqual(one_free_poster_amount.getPrice(), 0)
    self.assertEqual(one_free_poster_amount.getResourceValue(), self.poster)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 9000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 450)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 9450)

    # even if we buy 3 CDs and 1 DVD, only one poster will be given.
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_3,
                                    quantity=1,
                                    price=2400)
    self.appendBaseContributionCategory(order_line_3, self.poster_present_3cd)

    self.stepTic()

    # check again
    one_free_poster_amount = self.getAmount(order,
                                            '3CD_OR_1DVD_GET_1_POSTER_FREE',
                                            return_object=True)
    self.assertEqual(one_free_poster_amount.getTotalPrice(), 0)
    self.assertEqual(one_free_poster_amount.getQuantity(), 1)
    self.assertEqual(one_free_poster_amount.getPrice(), 0)
    self.assertEqual(one_free_poster_amount.getResourceValue(), self.poster)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 11400)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 570)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 11970)

  def test_usecase5(self):
    """
    Use case 5 : Buy 3 CDs or more, 1 highest priced DVD in ordered 15% off.

    1 DVD    3000 yen
    1 DVD    1000 yen
    2 CD    10000 yen
    1 CD     3000 yen
    discount 3000 * 0.15 = 450 yen
    """
    createZODBPythonScript(
      self.portal.portal_skins.custom,
      'TradeModelLine_calculate3CD15PercentDiscountOf1HighestPricedDVD',
      'current_aggregated_amount_list, current_movement, aggregated_movement_list',
      '''\
total_quantity = sum([movement.getQuantity() for movement in aggregated_movement_list])
if total_quantity >= 3:
  price_dvd_list = []
  product_line_dvd = context.portal_categories.product_line.video.dvd
  for movement in current_aggregated_amount_list:
    resource = movement.getResourceValue()
    if resource.getProductLineValue() == product_line_dvd:
      price_dvd_list.append((movement.getPrice(), movement))
  if price_dvd_list:
    price_dvd_list.sort()
    highest_priced_dvd_movement = price_dvd_list[-1][1]
    total_price = highest_priced_dvd_movement.getTotalPrice()

    from Products.ERP5Type.Document import newTempSimulationMovement
    causality_value_list = list(aggregated_movement_list) + [highest_priced_dvd_movement]
    temporary_movement = newTempSimulationMovement(current_movement.getParentValue(), current_movement.getId())
    temporary_movement.edit(title=current_movement.getProperty('title'),
                            description=current_movement.getProperty('description'),
                            resource=current_movement.getProperty('resource'),
                            reference=current_movement.getProperty('reference'),
                            int_index=current_movement.getProperty('int_index'),
                            base_application_list=current_movement.getProperty('base_application_list'),
                            base_contribution_list=current_movement.getProperty('base_contribution_list'),
                            start_date=highest_priced_dvd_movement.getStartDate(),
                            stop_date=highest_priced_dvd_movement.getStopDate(),
                            create_line=current_movement.getProperty('is_create_line'),
                            trade_phase_list=current_movement.getTradePhaseList(),
                            causality_list=[movement.getRelativeUrl() for movement in causality_value_list])
    temporary_movement.setPrice(current_movement.getProperty('price'))
    temporary_movement.setQuantity(highest_priced_dvd_movement.getPrice())
    return temporary_movement
''')
    order = self.createOrder()
    order.edit(specialise_value=self.trade_condition)
    order.Order_applyTradeCondition(order.getSpecialiseValue())
    order.newContent(portal_type='Trade Model Line',
                     reference='3CD_AND_1HIGHEST_PRICED_DVD_15PERCENT_OFF',
                     resource_value=self.service_discount,
                     price=-0.15,
                     quantity=None,
                     efficiency=1,
                     target_level=TARGET_LEVEL_DELIVERY,
                     calculation_script_id='TradeModelLine_calculate3CD15PercentDiscountOf1HighestPricedDVD',
                     create_line=True,
                     trade_phase=None,
                     base_application_value_list=[self.special_discount_3cd],
                     base_contribution_value_list=[self.discount_amount_of_vat_taxable])

    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_1,
                                    quantity=1,
                                    price=3000)
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.movie_dvd_2,
                                    quantity=1,
                                    price=1000)
    order_line_3 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_1,
                                    quantity=1,
                                    price=5000)
    self.appendBaseContributionCategory(order_line_3, self.special_discount_3cd)
    order_line_4 = order.newContent(portal_type=self.order_line_portal_type,
                                    resource_value=self.music_album_2,
                                    quantity=1,
                                    price=3000)
    self.appendBaseContributionCategory(order_line_4, self.special_discount_3cd)

    self.stepTic()

    # check the current amount
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 12000)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 600)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'),
                     12600)
    # add one more cd, then total is 3. the special discount will be applied.
    order_line_3.setQuantity(2)

    self.stepTic()

    # check again
    self.assertEqual(self.getAmount(order, '3CD_AND_1HIGHEST_PRICED_DVD_15PERCENT_OFF'),
                     -450)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITHOUT_VAT'), 16550)
    self.assertEqual(self.getAmount(order, 'VAT_AMOUNT'), 827.5)
    self.assertEqual(self.getAmount(order, 'TOTAL_PRICE_WITH_VAT'), 17377.5)


class TestTradeModelLineSale(TestTradeModelLine):
  invoice_portal_type = 'Sale Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_transaction_line_portal_type = 'Sale Invoice Transaction Line'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  packing_list_portal_type = 'Sale Packing List'
  trade_condition_portal_type = 'Sale Trade Condition'


class TestTradeModelLinePurchase(TestTradeModelLine):
  invoice_portal_type = 'Purchase Invoice Transaction'
  invoice_line_portal_type = 'Invoice Line'
  invoice_transaction_line_portal_type = 'Purchase Invoice Transaction Line'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  packing_list_portal_type = 'Purchase Packing List'
  trade_condition_portal_type = 'Purchase Trade Condition'


class TestComplexTradeModelLineUseCaseSale(TestComplexTradeModelLineUseCase):
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  trade_condition_portal_type = 'Sale Trade Condition'


class TestComplexTradeModelLineUseCasePurchase(TestComplexTradeModelLineUseCase):
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  trade_condition_portal_type = 'Purchase Trade Condition'


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestTradeModelLineSale))
  suite.addTest(unittest.makeSuite(TestTradeModelLinePurchase))
  suite.addTest(unittest.makeSuite(TestComplexTradeModelLineUseCaseSale))
  suite.addTest(unittest.makeSuite(TestComplexTradeModelLineUseCasePurchase))
  return suite
