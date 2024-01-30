# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009-2010 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#          Fabien Morin <fabien@nexedi.com>
#          Julien Muchembled <jm@nexedi.com>
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

from six.moves import UserDict
import functools
import random
import unittest
from unittest import expectedFailure

from erp5.component.test.testBPMCore import TestBPMMixin
from Products.ERP5Type.Base import Base
from Products.ERP5Type.Utils import simple_decorator
from DateTime import DateTime
from Products.ERP5Type.tests.utils import createZODBPythonScript
from Products.ERP5OOo.tests.utils import Validator
import six


def save_result_as(name):
  @simple_decorator
  def decorator(function):
    def wrapper(self, *args, **kw):
      result = function(self, *args, **kw)
      self[name] = result
      return result
    return wrapper
  return decorator


class TestTradeModelLineMixin(TestBPMMixin, UserDict):
  """Provides methods to implementations sharing similar logic to Trade Model Lines"""
  # Constants and variables shared by tests
  base_unit_quantity = 0.01
  node_portal_type = 'Organisation'
  order_date = DateTime()
  amount_generator_line_portal_type = 'Trade Model Line'

  # XXX so that unittest.suite._isnotsuite return False
  def __iter__(self):
    raise TypeError()

  def setBaseAmountQuantityMethod(self, base_amount_id, text):
    """Populate TradeModelLine_getBaseAmountQuantityMethod shared script

    This helper method edits the script so that:
    - there's no need to do any cleanup
    - data produced by previous still behaves as expected
    """
    base_amount = self.portal.portal_categories.base_amount
    for name in self.__class__.__name__, self._testMethodName:
      try:
        base_amount = base_amount[name]
      except KeyError:
        base_amount = base_amount.newContent(name)
    try:
      return base_amount[base_amount_id].getRelativeUrl()
    except KeyError:
      base_amount = base_amount.newContent(base_amount_id).getRelativeUrl()
    skin = self.portal.portal_skins.custom
    script_id = self.amount_generator_line_portal_type.replace(' ', '') \
                + '_getBaseAmountQuantityMethod'
    test = "\nif base_application == %r:\n  " % base_amount
    try:
      old_text = '\n' + skin[script_id].body()
    except KeyError:
      old_text = ''
    else:
      skin._delObject(script_id)
    text = test + '\n  '.join(text.splitlines()) + old_text
    createZODBPythonScript(skin, script_id, "base_application", text)
    return base_amount

  def afterSetUp(self):
    UserDict.__init__(self)
    self.portal.portal_preferences.getActiveSystemPreference().setPreferredTaxUseList(['use/tax'])
    self.tic()
    return super(TestTradeModelLineMixin, self).afterSetUp()

  def clone(self, document):
    parent = document.getParentValue()
    clone, = parent.manage_pasteObjects(
      parent.manage_copyObjects(ids=document.getId()))
    clone = parent[clone['new_id']]
    try:
      self[clone.getPath()] = self[document.getPath()]
    except KeyError:
      pass
    return clone

  @save_result_as('node')
  def createNode(self, **kw):
    module = self.portal.getDefaultModule(portal_type=self.node_portal_type)
    return module.newContent(portal_type=self.node_portal_type, **kw)

  @save_result_as('resource')
  def createResource(self, portal_type, **kw):
    module = self.portal.getDefaultModule(portal_type=portal_type)
    return module.newContent(portal_type=portal_type, **kw)

  @save_result_as('currency')
  def createCurrency(self):
    return self.createResource('Currency', title='Currency',
                               base_unit_quantity=self.base_unit_quantity)

  @save_result_as('business_process')
  def createBusinessProcess(self, **kw):
    business_process = super(TestTradeModelLineMixin,
        self).createBusinessProcess(**kw)
    if self.business_link_portal_type is not None:
      business_link_list = [
        dict(reference='discount',
             trade_phase='trade/discount',
             predecessor='trade_state/invoiced',
             # should successor be trade_state/discounted? There is no
             # such trade_state category
             successor='trade_state/accounted',
             delivery_builder=['portal_deliveries/purchase_invoice_transaction_trade_model_builder',
                               'portal_deliveries/sale_invoice_transaction_trade_model_builder'],
        ),
        dict(reference='tax',
             trade_phase='trade/tax',
             predecessor='trade_state/invoiced',
             # should successor be trade_state/taxed? There IS such a
             # trade_state category, but the rule that wants to match
             # the Simulation Movement that has this link as causality
             # is default_invoice_transaction_rule, the same as for
             # default/discount, so I'll use the same successor as
             # above. Besides, we'd have to create a new business_link
             # just to get back to accounted, and match it with (or
             # create a new) a portal_rule.
             successor='trade_state/accounted',
             delivery_builder=['portal_deliveries/purchase_invoice_transaction_trade_model_builder',
                               'portal_deliveries/sale_invoice_transaction_trade_model_builder'],
        ),
      ]
      for business_link in business_link_list:
        link = self.createBusinessLink(business_process, **business_link)
        self['business_link/' + link.getTradePhaseId()] = link
    return business_process

  @save_result_as('trade_condition')
  def createTradeCondition(self, specialise_value_list,
                           trade_model_line_list=(), **kw):
    module = self.portal.getDefaultModule(
        portal_type=self.trade_condition_portal_type)
    if isinstance(specialise_value_list, Base):
      specialise_value_list = specialise_value_list,
    trade_condition = module.newContent(
        portal_type=self.trade_condition_portal_type,
        title=self.id(),
        specialise_value_list=specialise_value_list,
        **kw)
    for kw in trade_model_line_list:
      self.createTradeModelLine(trade_condition, **kw)
    return trade_condition

  def createTradeModelLine(self, document, **kw):
    line = document.newContent(portal_type='Trade Model Line', **kw)
    reference = line.getReference()
    if reference:
      self['trade_model_line/' + reference] =  line
    return line

  @save_result_as('order')
  def createOrder(self, specialise_value_list, order_line_list=(), **kw):
    module = self.portal.getDefaultModule(portal_type=self.order_portal_type)
    if isinstance(specialise_value_list, Base):
      specialise_value_list = specialise_value_list,
    kw.setdefault('start_date', self.order_date)
    order = module.newContent(
        portal_type=self.order_portal_type,
        title=self.id(),
        specialise_value_list=specialise_value_list,
        **kw)
    for arrow in ('source_value', 'source_section_value',
                  'destination_value', 'destination_section_value'):
      if order.getProperty(arrow) is None:
        order._setProperty(arrow, self.createNode())
    if not order.getPriceCurrency():
      self['price_currency'] = price_currency = self.createCurrency()
      order._setPriceCurrencyValue(price_currency)
    for line_kw in order_line_list:
      order.newContent(portal_type=self.order_line_portal_type, **line_kw)
    return order

  def getAggregatedAmountList(self, amount_generator, *args, **kw):
    return amount_generator.getAggregatedAmountList(*args, **kw)

  def getAggregatedAmountDict(self, amount_generator, partial_check=False,
                              **expected_amount_dict):
    amount_list = self.getAggregatedAmountList(amount_generator)
    amount_dict = {}
    for amount in amount_list:
      reference = amount.getReference()
      try:
        expected_amount = expected_amount_dict.pop(reference)
      except KeyError:
        if not partial_check:
          raise
      else:
        for k, v in six.iteritems(expected_amount):
          if k == 'causality_value_list':
            self.assertEqual(v, amount.getValueList('causality'))
          else:
            self.assertEqual(v, amount.getProperty(k))
        amount_dict[reference] = amount
    if partial_check:
      for value in six.itervalues(expected_amount_dict):
        self.assertEqual(None, value)
    else:
      self.assertEqual({}, expected_amount_dict)
    return amount_dict

  def getTradeModelSimulationMovementList(self, delivery_line):
    result_list = []
    for simulation_movement in delivery_line.getDeliveryRelatedValueList(
        portal_type='Simulation Movement'):
      if delivery_line.getPortalType() == self.order_line_portal_type:
        applied_rule, = [x
          for x in simulation_movement.objectValues()
          if x.getSpecialiseReference() == 'default_delivering_rule']
        simulation_movement, = applied_rule.objectValues()
      applied_rule, = [x
        for x in simulation_movement.objectValues()
        if x.getSpecialiseReference() == 'default_invoicing_rule']
      simulation_movement, = applied_rule.objectValues()
      applied_rule, = [x
        for x in simulation_movement.objectValues()
        if x.getSpecialiseReference() == 'default_trade_model_rule']
      result_list.append(applied_rule.objectValues())
    return result_list


class TestTradeModelLine(TestTradeModelLineMixin):

  # Constants and variables shared by tests
  default_discount_ratio = -0.05 # -5%
  default_tax_ratio = 0.196 # 19,6%

  new_discount_ratio = -0.04 # -4%
  new_tax_ratio = 0.22 # 22%

  modified_order_line_price_ratio = 2.0
  modified_packing_list_line_quantity_ratio = 0.4
  modified_invoice_line_quantity_ratio = modified_order_line_quantity_ratio \
      = 2.5

  @save_result_as('product/taxed')
  def createProductTaxed(self):
    return self.createResource('Product',
      title='Product Taxed',
      base_contribution=['base_amount/tax'],
      use='normal')

  @save_result_as('product/discounted')
  def createProductDiscounted(self):
    return self.createResource('Product',
      title='Product Discounted',
      base_contribution=['base_amount/discount'],
      use='normal')

  @save_result_as('product/taxed_discounted')
  def createProductDiscountedTaxed(self):
    return self.createResource('Product',
      title='Product Discounted & Taxed',
      base_contribution=['base_amount/discount', 'base_amount/tax'],
      use='normal')

  @save_result_as('service/tax')
  def createServiceTax(self):
    return self.createResource('Service', title='Tax', use='tax')

  @save_result_as('service/discount')
  def createServiceDiscount(self):
    return self.createResource('Service', title='Discount', use='discount')

  def packPackingList(self, packing_list):
    if packing_list.getContainerState() == 'packed':
      return
    packing_list.manage_delObjects(ids=[q.getId()
      for q in packing_list.objectValues(portal_type='Container')])
    self.commit()
    container = packing_list.newContent(portal_type='Container')
    for movement in packing_list.getMovementList():
      container.newContent(portal_type='Container Line',
                           resource=movement.getResource(),
                           quantity=movement.getQuantity())
    self.tic()
    self.assertEqual('packed', packing_list.getContainerState())

  def copyExpectedAmountDict(self, delivery, ratio=1):
    self[delivery.getPath()] = expected_amount_dict = {}
    causality = delivery.getCausalityValue()
    for base_amount, amount_dict in six.iteritems(self[causality.getPath()]):
      expected_amount_dict[base_amount] = new_amount_dict = {}
      for line in delivery.getMovementList():
        line_id = line.getCausalityId()
        if line_id in amount_dict:
          new_amount_dict[line.getId()] = ratio * amount_dict[line_id]

  def acceptDecisionQuantityInvoice(self, invoice):
    solver_process_tool = self.portal.portal_solver_processes
    solver_process = solver_process_tool.newSolverProcess(invoice)
    for quantity_solver_decision in solver_process.contentValues():
      if quantity_solver_decision.getCausalityValue().getTestedProperty() \
        == 'quantity':
        # use Trade Model Solver.
        quantity_solver_decision.setSolverValue(
          self.portal.portal_solvers['Trade Model Solver'])
    solver_process.buildTargetSolverList()
    solver_process.solve()

  def processPackingListBuildInvoice(self, packing_list, build=None):
    self.packPackingList(packing_list)
    self.tic()

    packing_list.start()
    packing_list.stop()
    self.tic()
    self.buildInvoices()
    self.tic()

    invoice, = packing_list.getCausalityRelatedValueList(
      portal_type=self.invoice_portal_type)
    self.assertEqual(5, len(invoice))

    packing_list.deliver()
    self.tic()

    self['invoice'] = invoice
    if build == 'invoice':
      return invoice

    self.checkCausalityState(invoice, 'solved')
    self.checkTradeModelRuleSimulationExpand(packing_list)

    invoice.start()
    self.tic()

    self.checkInvoiceAccountingMovements(invoice)

  ###
  ##  Check methods
  ##

  def checkWithoutBPM(self, order):
    self.commit()# clear transactional cache
    order.getSpecialiseValue()._setSpecialise(None)
    self.assertRaises(ValueError, order.getCausalityRelatedValue(
      portal_type='Applied Rule').expand, 'immediate')
    self.abort()

  def checkModelLineOnDelivery(self, delivery):
    for portal_type in (self.business_link_portal_type,
                        self.trade_model_path_portal_type,
                        'Trade Model Line'):
      self.assertRaises(ValueError, delivery.newContent,
                        portal_type=portal_type)

  def checkComposition(self, movement, specialise_value_list, type_count_dict):
    composed = movement.asComposedDocument()
    self.assertNotIn(movement, composed._effective_model_list)
    self.assertSameSet(composed.getSpecialiseValueList(),
                       specialise_value_list)
    count = 0
    for portal_type, n in six.iteritems(type_count_dict):
      count += n
      self.assertEqual(n, len(composed.objectValues(portal_type=portal_type)))
    self.assertTrue(count, len(composed.objectValues()))

  def checkAggregatedAmountList(self, order):
    expected_result_dict = self[order.getPath()]
    def check(movement, movement_id):
      kw = {}
      for reference, result in six.iteritems(expected_result_dict):
        total_price = result.get(movement_id) or 0.0
        if True:
          model_line = self['trade_model_line/' + reference]
          kw[reference] = dict(total_price=total_price,
            causality_value_list=[model_line],
            base_application_list=model_line.getBaseApplicationList(),
            base_contribution_list=model_line.getBaseContributionList())
      self.getAggregatedAmountDict(movement, **kw)

    check(order, None)
    for line in order.getMovementList():
      check(line, line.getId())

  def checkTradeModelRuleSimulationExpand(self, delivery):
    expected_result_dict = self[delivery.getPath()]

    for line in delivery.getMovementList():
      simulation_movement_list_list = self.getTradeModelSimulationMovementList(line)
      self.assertEqual(len(simulation_movement_list_list), 1)
      simulation_movement_list = simulation_movement_list_list[0]
      result_dict = {sm.getResourceValue().getUse(): sm
                     for sm in simulation_movement_list}
      self.assertEqual(len(simulation_movement_list),
                       len(result_dict))
      for use in 'discount', 'tax':
        total_price = expected_result_dict[use].get(line.getId()) or 0.0
        if True:
          sm = result_dict.pop(use)
          self.assertEqual(str(sm.getTotalPrice() or 0.0), str(total_price))
          self.assertEqual(3, len(sm.getCausalityValueList()))
          self.assertEqual(1, len(sm.getCausalityValueList(
            portal_type=self.business_link_portal_type)))
          self.assertEqual(1, len(sm.getCausalityValueList(
            portal_type=self.trade_model_path_portal_type)))
          self.assertEqual(1, len(sm.getCausalityValueList(
            portal_type='Trade Model Line')))
          self.assertEqual(sm.getBaseApplicationList(),
                           ['base_amount/' + use])
          self.assertEqual(sm.getBaseContributionList(),
                           dict(discount=['base_amount/tax'], tax=[])[use])
      self.assertEqual({}, result_dict)

  def checkCausalityState(self, delivery, state):
    self.assertEqual(state, delivery.getCausalityState(),
      delivery.getDivergenceList())

  def checkInvoiceAccountingMovements(self, invoice):
    # Wouldn't it be better to use 'invoice.getAggregatedAmountList()'
    # instead of looking at invoice lines ? We wouldn't have to clear
    # base_contribution_list in test_01a_InvoiceNewTradeConditionOrLineSupport
    line_dict = {}
    for line in invoice.getMovementList():
      if line.getPortalType() == self.invoice_line_portal_type:
        key = line.getResourceValue().getUse()
      else:
        key = ('income_expense', 'payable_receivable', 'vat')[
          ['income', 'expense',
           'liability/payable', 'asset/receivable',
           'liability/payable/collected_vat', 'asset/receivable/refundable_vat',
          ].index(line.getSourceValue().getAccountType()) // 2]
      line_dict.setdefault(key, 0)
      line_dict[key] += line.getTotalPrice()
    self.assertEqual(6, len(line_dict))

    currency_precision = self['price_currency'].getQuantityPrecision()
    rounded_total_price = round(line_dict['normal'], currency_precision)
    rounded_tax_price = round(line_dict['tax'], currency_precision)
    rounded_discount_price = round(line_dict['discount'], currency_precision)
    self.assertEqual(str(abs(line_dict['payable_receivable'])),
        str(rounded_total_price + rounded_tax_price + rounded_discount_price))
    self.assertEqual(str(abs(line_dict['vat'])),
        str(rounded_tax_price))
    self.assertEqual(str(abs(line_dict['income_expense'])),
        str(rounded_total_price + rounded_discount_price))

  def buildPackingLists(self):
    self.portal.portal_alarms.packing_list_builder_alarm.activeSense()
    self.tic()

  def buildInvoices(self):
    self.portal.portal_alarms.invoice_builder_alarm.activeSense()
    self.tic()

  ###
  ##  Test cases
  ##

  def test_01_OrderWithSimpleTaxedAndDiscountedLines(self, build=None):
    """Full test case with quite simple linear use case

    Data:
    - 1 SO: 1 taxed, 1 discounted, 1 taxed&discounted
    - 1 TC: tax, discount
    - 1 BP (linked to default BP)

    Checks:
    - composition
    - getAggregatedAmountList
    - expand (before and after modifying quantities on order lines)
    - build of packing list (+ pack) and invoice
    """
    taxed = self.createProductTaxed()
    discounted = self.createProductDiscounted()
    taxed_discounted = self.createProductDiscountedTaxed()
    business_process = self.createBusinessProcess()
    trade_condition = self.createTradeCondition(
      business_process, (
      dict(price=self.default_discount_ratio,
           base_application='base_amount/discount',
           base_contribution='base_amount/tax',
           trade_phase='trade/discount',
           resource_value=self.createServiceDiscount(),
           reference='discount'),
      dict(price=self.default_tax_ratio,
           base_application='base_amount/tax',
           trade_phase='trade/tax',
           resource_value=self.createServiceTax(),
           reference='tax'),
      ))
    order = self.createOrder(trade_condition, (
      dict(price=1, quantity=2, id='taxed',
                                resource_value=taxed),
      dict(price=3, quantity=4, id='discounted',
                                resource_value=discounted),
      dict(price=5, quantity=6, id='taxed_discounted',
                                resource_value=taxed_discounted),
      ))
    discount = {None: (3*4 + 5*6) * self.default_discount_ratio,
                'discounted': (3*4) * self.default_discount_ratio,
                'taxed_discounted': (5*6) * self.default_discount_ratio}
    self[order.getPath()] = dict(
      discount=discount,
      tax={None: (1*2 + 5*6 + discount[None]) * self.default_tax_ratio,
           'taxed': (1*2) * self.default_tax_ratio,
           'discounted': discount['discounted'] * self.default_tax_ratio,
           'taxed_discounted': (5*6 + discount['taxed_discounted'])
                               * self.default_tax_ratio})

    self.tic()

    if not build:
      for movement in (order, order['taxed'], order['discounted'],
                       order['taxed_discounted']):
        self.checkComposition(movement, [trade_condition], {
          self.trade_model_path_portal_type: 12,
          self.business_link_portal_type: 7,
          "Trade Model Line": 2})

      self.checkAggregatedAmountList(order)

      order.plan()
      self.tic()

      self.checkTradeModelRuleSimulationExpand(order)

      self.checkWithoutBPM(order)

      order2 = self.clone(order)

      # Multiply prices by 2 and quantities by 2.5
      order['taxed'].edit(price=2, quantity=5)
      order['discounted'].edit(price=6, quantity=10)
      order['taxed_discounted'].edit(price=10, quantity=15)
      self.tic()

      discount = {None: (6*10 + 10*15) * self.default_discount_ratio,
                  'discounted': (6*10) * self.default_discount_ratio,
                  'taxed_discounted': (10*15) * self.default_discount_ratio}
      self[order.getPath()] = dict(
        discount=discount,
        tax={None: (2*5 + 10*15 + discount[None]) * self.default_tax_ratio,
             'taxed': (2*5) * self.default_tax_ratio,
             'discounted': discount['discounted'] * self.default_tax_ratio,
             'taxed_discounted': (10*15 + discount['taxed_discounted'])
                                 * self.default_tax_ratio})

      self.checkTradeModelRuleSimulationExpand(order)

      self.checkAggregatedAmountList(order)
      order = order2

    order.confirm()
    self.tic()
    self.buildPackingLists()

    packing_list, = order.getCausalityRelatedValueList(
      portal_type=self.packing_list_portal_type)
    self.copyExpectedAmountDict(packing_list)

    self['packing_list'] = packing_list
    if build == 'packing_list':
      return packing_list

    return self.processPackingListBuildInvoice(packing_list, build)

  def test_01a_InvoiceNewTradeConditionOrLineSupport(self):
    invoice = self.test_01_OrderWithSimpleTaxedAndDiscountedLines('invoice')

    # on invoice, make specialise point to a new TC and check it diverged
    trade_condition = self['trade_condition']
    new_trade_condition = self.clone(trade_condition)
    line_dict = {line.getReference(): line
                 for line in new_trade_condition.objectValues()}
    line_dict['discount'].edit(reference='discount_2',
                               price=self.new_discount_ratio)
    line_dict['tax'].edit(reference='tax_2',
                          price=self.new_tax_ratio)

    self.assertEqual([trade_condition], invoice.getSpecialiseValueList())
    invoice.setSpecialiseValue(new_trade_condition)
    self.tic()
    self.checkCausalityState(invoice, 'diverged')

    # revert to reuse invoice
    invoice.setSpecialiseValue(trade_condition)
    self.tic()
    self.checkCausalityState(invoice, 'solved')

    # check how is supported addition of invoice line to invoice
    for line in self['order'].getMovementList():
      line = invoice.newContent(portal_type=self.invoice_line_portal_type,
                                resource=line.getResource(),
                                quantity=line.getQuantity(),
                                price=line.getPrice())
      # XXX base_contribution_list is automatically copied from the resource
      #     but Invoice Transaction Trade Model Line Builder will not be called
      #     again (or if we call it, lines would be built in a new invoice)
      #     and accounting lines would not match invoice lines.
      #     So we clear the list to make the test simpler.
      #     See also 'checkInvoiceAccountingMovements' method.
      self.assertTrue(line.getBaseContributionList())
      line._setBaseContributionList(())
    self.tic()
    self.checkCausalityState(invoice, 'solved')

    invoice.start()
    self.tic()

    self.checkCausalityState(invoice, 'solved')
    self.checkInvoiceAccountingMovements(invoice)

    invoice.stop()
    invoice.deliver()
    self.tic()

  def test_01b_NewSimulation_InvoiceModifyQuantityAndSolveDivergency(self):
    invoice = self.test_01_OrderWithSimpleTaxedAndDiscountedLines('invoice')

    for line in invoice.getMovementList():
      if line.getResourceValue().getUse() == 'normal':
        line.setQuantity(line.getQuantity() *
          self.modified_invoice_line_quantity_ratio)
    self.tic()
    self.checkCausalityState(invoice, 'diverged')

    self.acceptDecisionQuantityInvoice(invoice)
    self.tic()
    self.checkCausalityState(invoice, 'solved')

  def test_01c_PackingListSplitBuildInvoiceBuild(self):
    packing_list = \
      self.test_01_OrderWithSimpleTaxedAndDiscountedLines('packing_list')

    for line in packing_list.getMovementList():
      line.setQuantity(line.getQuantity() *
          self.modified_packing_list_line_quantity_ratio)
    self.tic()
    self.checkCausalityState(packing_list, 'diverged')

    order = self['order']
    self.checkTradeModelRuleSimulationExpand(order)
    self.copyExpectedAmountDict(packing_list,
        self.modified_packing_list_line_quantity_ratio)
    solver_process = self.portal.portal_solver_processes.newSolverProcess(packing_list)
    quantity_solver_decision_list = [x for x in solver_process.contentValues()
        if x.getCausalityValue().getTestedProperty() == 'quantity']
    self.assertTrue(quantity_solver_decision_list)
    for quantity_solver_decision in quantity_solver_decision_list:
      # use Quantity Split Solver.
      quantity_solver_decision.setSolverValue(self.portal.portal_solvers['Quantity Split Solver'])
      # configure for Quantity Split Solver.
      kw = {
          'delivery_solver': 'FIFO Delivery Solver',
          'start_date': packing_list.getStartDate() + 15,
          'stop_date': packing_list.getStopDate() + 25,
      }
      quantity_solver_decision.updateConfiguration(**kw)
    solver_process.buildTargetSolverList()
    solver_process.solve()
    self.tic()
    self.buildPackingLists()
    self.tic()
    self.checkCausalityState(packing_list, 'solved')
    new_packing_list, = [x for x in order.getCausalityRelatedValueList(
                             portal_type=self.packing_list_portal_type)
                           if x != packing_list]
    self.copyExpectedAmountDict(new_packing_list,
        1 - self.modified_packing_list_line_quantity_ratio)

    invoice_count = len(self.portal
        .accounting_module.objectValues(portal_type=self.invoice_portal_type))
    self.processPackingListBuildInvoice(packing_list)
    # For some time, the following assertion failed. Here was the reason:
    #     With legacy code, only 1 invoice was built after starting the first
    #     packing list. Now, all invoice lines generated by trade model are
    #     built immediately, creating a second invoice before starting the
    #     second packing list, and we end up with 3 invoices. In other words,
    #     the new simulation splits the second invoice, and I am not sure it's
    #     correct.
    #     The difference between old and new simulation is that when the first
    #     invoice is confirmed, the old code does not expand the simulation
    #     tree completely and SaleInvoice_selectTradeModelMovementList can't
    #     find any simulation movements related to the second packing list.
    # This was fixed by removing 'planned' state from
    # {Purchase,Sale}Invoice_selectTradeModelMovementList scripts.
    self.assertEqual(invoice_count + 1, len(self.portal
        .accounting_module.objectValues(portal_type=self.invoice_portal_type)))
    self.processPackingListBuildInvoice(new_packing_list)

  def test_02_OrderWithComplexTaxedAndDiscountedLines(self):
    service_discount = self.createServiceDiscount()
    service_tax = self.createServiceTax()
    business_process = self.createBusinessProcess()
    line_list = [
      dict(price=0.2,
           base_application='base_amount/tax',
           base_contribution='base_amount/total_tax',
           trade_phase='trade/tax',
           resource_value=service_tax,
           reference='service_tax'),
      dict(price=0.32,
           base_application='base_amount/discount',
           base_contribution='base_amount/total_discount',
           trade_phase='trade/discount',
           resource_value=service_discount,
           reference='total_dicount_2'),
      dict(price=0.2,
           base_application='base_amount/tax',
           base_contribution='base_amount/total_tax',
           trade_phase='trade/tax',
           resource_value=service_tax,
           reference='service_tax_2'),
      dict(price=0.12,
           base_application='base_amount/total_tax',
           base_contribution='base_amount/total_discount',
           trade_phase='trade/tax',
           resource_value=service_tax,
           reference='tax_3'),
      dict(price=0.8,
           base_application='base_amount/total_discount',
           trade_phase='trade/discount',
           resource_value=service_discount,
           reference='total_discount'),
      ]
    random.shuffle(line_list)
    trade_condition = self.createTradeCondition(business_process, line_list)

    taxed = self.createProductTaxed()
    discounted = self.createProductDiscounted()
    order = self.createOrder(trade_condition, (
      dict(price=1, quantity=2, id='taxed',
                                resource_value=taxed),
      dict(price=3, quantity=4, id='discounted',
                                resource_value=discounted),
      ))
    discount_price = (3*4) * 0.32
    tax_price = (1*2) * 0.2
    total_tax_price = tax_price * 2 * 0.12
    self[order.getPath()] = dict(
      service_tax={None: tax_price, 'taxed': tax_price},
      total_dicount_2={None: discount_price, 'discounted': discount_price},
      service_tax_2={None: tax_price, 'taxed': tax_price},
      tax_3={None: total_tax_price, 'taxed': total_tax_price},
      total_discount={None: (total_tax_price+discount_price) * 0.8,
                      'taxed': total_tax_price * 0.8,
                      'discounted': discount_price * 0.8})

    self.tic()

    self.checkModelLineOnDelivery(order)

    for movement in order, order['taxed'], order['discounted']:
      self.checkComposition(movement, [trade_condition], {
        self.trade_model_path_portal_type: 12,
        self.business_link_portal_type: 7,
        "Trade Model Line": 5})

    self.checkAggregatedAmountList(order)

  def test_03_VariatedModelLine(self):
    base_amount = self.setBaseAmountQuantityMethod('tax', """\
def getBaseAmountQuantity(delivery_amount, base_application,
                          variation_category_list=(), **kw):
  if variation_category_list:
    quantity = delivery_amount.getGeneratedAmountQuantity(base_application)
    tax_range, = variation_category_list
    if tax_range == 'tax_range/0_200':
      return min(quantity, 200)
    else:
      assert tax_range == 'tax_range/200_inf'
      return max(0, quantity - 200)
  return context.getBaseAmountQuantity(delivery_amount, base_application, **kw)
return getBaseAmountQuantity""")
    business_process = self.createBusinessProcess()
    trade_condition = self.createTradeCondition(business_process, (
      dict(price=0.3,
           base_application=base_amount,
           reference='tax1'),
      dict(base_application=base_amount,
           base_contribution='base_amount/total_tax',
           reference='tax2'),
      dict(base_application='base_amount/total_tax',
           base_contribution='base_amount/total',
           reference='tax3'),
      ))
    def createCells(line, matrix, base_application=(), base_contribution=()):
      range_list = [set() for x in next(iter(matrix))]
      for index in matrix:
        for x, y in zip(range_list, index):
          x.add(y)
      line.setCellRange(*range_list)
      for index, price in six.iteritems(matrix):
        line.newCell(mapped_value_property='price', price=price,
          base_application_list=[index[i] for i in base_application],
          base_contribution_list=[index[i] for i in base_contribution],
          *index)
    createCells(self['trade_model_line/tax2'], {
      ('tax_range/0_200', 'tax_share/A'): .1,
      ('tax_range/0_200', 'tax_share/B'): .2,
      ('tax_range/200_inf', 'tax_share/A'): .3,
      ('tax_range/200_inf', 'tax_share/B'): .4,
      }, base_application=(0,), base_contribution=(1,))
    createCells(self['trade_model_line/tax3'], {
      ('tax_share/A',): .5,
      ('tax_share/B',): .6,
      }, base_application=(0,))
    for x in ((100, 30, 10, 0, 0, 20, 5, 12),
              (500, 150, 20, 90, 40, 120, 55, 96)):
      amount = self.portal.newContent(temp_object=True, portal_type='Amount', id='_',
                            quantity=x[0], price=1,
                            base_contribution=base_amount)
      amount_list = trade_condition.getGeneratedAmountList((amount,))
      self.assertEqual(sorted(x[1:]),
                       sorted(y.getTotalPrice() for y in amount_list))

  def test_04_cumulativePriceAdjustment(self):
    """
      Check a trade condition with 3 discounts that are applied one after the
      other using a single base_amount category and trivial dependencies
      between trade model lines, which can even be unordered.

      The 10%, 40% & 30% discounts result in an overall 62.2% discount,
      and not 80%.
    """
    base_amount = self.setBaseAmountQuantityMethod('cumulative', """\
return lambda delivery_amount, base_application, **kw: \\
  delivery_amount.getTotalPrice() + \\
  delivery_amount.getAmountQuantity(base_application)""")
    discount_list = .1, .4, .3
    tax = self.createServiceTax()
    trade_condition = self.createTradeCondition((), (
      dict(reference='tax', resource_value=tax, price=.2,
           base_application='base_amount/tax'),
      ))
    for discount in discount_list:
      self.createTradeModelLine(trade_condition,
        resource_value=self.createResource('Service', use='discount'),
        price=-discount)
    createZODBPythonScript(trade_condition, "TradeModelLine_asPredicate",
                           "", """\
if not context.getReference():
  relative_url = context.getResourceValue().getRelativeUrl()
  context = context.asContext()
  context.setReference(relative_url)
  context.setBaseApplicationList((%r, relative_url))
  context.setBaseContributionList((%r, 'base_amount/tax'))
return context""" % (base_amount, base_amount))

    taxed = self.createProductTaxed()
    order = self.createOrder(trade_condition, (
      dict(price=1, quantity=2, resource_value=taxed),
      dict(price=3, quantity=4, resource_value=taxed),
      ))

    total_price = order.getTotalPrice()
    total_ratio = functools.reduce(lambda x, y: x*(1-y), discount_list, 1.2)
    amount_list = order.getAggregatedAmountList()
    self.assertAlmostEqual(total_price * total_ratio,
      sum((x.getTotalPrice() for x in amount_list), total_price))

  def test_05_dependencyResolution(self):
    from erp5.component.mixin.AmountGeneratorMixin import BaseAmountResolver
    delivery_amount = self.portal.newContent(temp_object=True, portal_type='Amount', id='')
    trade_model_line = self.portal.newContent(temp_object=True, portal_type='Trade Model Line', id='')
    def case(*lines):
      return BaseAmountResolver({}, {}), [{
        None: trade_model_line,
        'index': index,
        '_application': [(x, ()) for x in application],
        '_contribution': [(x, ()) for x in contribution],
      } for index, application, contribution in lines]
    def check():
      resolver(delivery_amount, property_dict_list)
      self.assertEqual(list(range(len(property_dict_list))),
                       [x['index'] for x in property_dict_list])

    # Case 1: calculation of some base_amount depends on others.
    trade_model_line.getBaseAmountQuantity = \
      lambda delivery_amount, base_amount: sum(map(
        delivery_amount.getGeneratedAmountQuantity,
        application_dict.get(base_amount, base_amount)))
    application_dict = dict(B='bf', C='c', E='Bef')
    resolver, property_dict_list = case((2, 'C', 'e'),
                                        (3, 'dE', ''),
                                        (0, 'a', 'b'),
                                        (1, 'B', 'cd'))
    check()
    # Retry with cache already filled.
    property_dict_list.reverse()
    check()
    del trade_model_line.getBaseAmountQuantity

    # Case 2: sorting by dependency resolution must be stable.
    # This is important for compatibility in case that calculation of D
    # applies d conditionally, whereas the user took care of ordering 3 after 2
    # with indices: 3 must remain after 2.
    resolver, property_dict_list = case((0, 'a', 'b'),
                                        (1, 'b', 'c'),
                                        (2, 'c', 'd'),
                                        (3, 'bD', ''))
    check()


  def test_tradeModelLineWithFixedPrice(self):
    """
      Check it's possible to have fixed quantity on lines. Sometimes we want
      to say "discount 10 euros" or "pay more 10 euros" instead of saying "10%
      discount from total"
    """
    fixed_quantity = self.setBaseAmountQuantityMethod('fixed_quantity', """\
return lambda *args, **kw: 1""")

    tax = self.createServiceTax()
    trade_condition = self.createTradeCondition((), (
      # create a model line with 100 euros
      dict(reference='A', resource_value=tax, quantity=100, price=1),
      # add a discount of 10 euros
      dict(reference='B', resource_value=tax, quantity=10, price=-1)))
    order = self.createOrder(trade_condition, (
      dict(),
      ))
    self.assertEqual([], order.getAggregatedAmountList())
    for line in trade_condition.objectValues():
      line.setBaseApplication(fixed_quantity)
    amount_list = order.getAggregatedAmountList()
    self.assertEqual([-10, 100], sorted(x.getTotalPrice() for x in amount_list))

  def test_BuildTradeModelLineAndAccountingFromOrder(self):
    business_process = self.createBusinessProcess()

    product = self.createProductTaxed()
    tax = self.createServiceTax()
    trade_condition = self.createTradeCondition(
      business_process, (
      dict(reference='VAT',
           price=.15,
           resource_value=tax,
           trade_phase='trade/tax',
           use='tax',
           base_application='base_amount/tax'),
      ))
    source = self.createNode()
    destination = self.createNode()

    order = self.createOrder(trade_condition, (
      dict(price=100, quantity=10, resource_value=product),
      ),
      source_value=source,
      destination_value=destination,
      source_section_value=source,
      destination_section_value=destination)

    def checkVATOnOrderPrintout(order):
      # BBB invoice printout has been improved to display
      # tax in a table grouping each tax togetherr, but order printout
      # not yet and uses a sligthly different data model
      data_dict = order._getTypeBasedMethod('getODTDataDict')()
      self.assertEqual(data_dict['total_price'], 1000.0)
      self.assertEqual(data_dict['total_price_novat'], 1000.0)
      self.assertEqual(
          [vat.getTotalPrice() for vat in data_dict['vat_list']], [150.0])
      # rendering template does not fail and is valid ODF
      self.assertFalse(
          Validator().validate(order._getTypeBasedMethod('viewAsODT')()))

    def checkVATOnInvoicePrintout(invoice):
      data_dict = invoice._getTypeBasedMethod('getODTDataDict')()
      self.assertEqual(data_dict['total_price_exclude_tax'], 1000.0)
      self.assertEqual(data_dict['total_tax_price'], 150.0)
      self.assertEqual(data_dict['total_price'], 1150.0)
      self.assertEqual(
          [
              (
                  line_tax['total_quantity'],
                  line_tax['base_price'],
                  line_tax['total_price'],
              ) for line_tax in data_dict['line_not_tax']
          ], [(10.0, 100.0, 1000.0)])
      self.assertEqual(
          [
              (
                  line_tax['total_quantity'],
                  line_tax['base_price'],
                  line_tax['total_price'],
              ) for line_tax in data_dict['line_tax']
          ], [(1000.0, 0.15, 150.0)])
      # rendering template does not fail and is valid ODF
      self.assertFalse(
          Validator().validate(order._getTypeBasedMethod('viewAsODT')()))

    checkVATOnOrderPrintout(order)
    order.plan()
    order.confirm()
    self.tic()
    self.buildPackingLists()
    checkVATOnOrderPrintout(order)

    packing_list = order.getCausalityRelatedValue(
                      portal_type=self.packing_list_portal_type)
    self.assertNotEqual(packing_list, None)
    self.assertEqual(1000, packing_list.getTotalPrice())

    packing_list.start()
    packing_list.stop()
    packing_list.deliver()
    self.tic()
    self.buildInvoices()

    invoice = packing_list.getCausalityRelatedValue(
                      portal_type=self.invoice_portal_type)
    self.assertNotEqual(invoice, None)
    self.assertEqual(2, len(invoice.getMovementList()))
    self.assertEqual(1150, invoice.getTotalPrice())
    self.assertEqual([], invoice.getDivergenceList())

    checkVATOnInvoicePrintout(invoice)
    invoice.start()
    self.tic()
    checkVATOnInvoicePrintout(invoice)
    self.assertEqual([], invoice.getDivergenceList())
    accounting_line_list = invoice.getMovementList(
             portal_type=self.invoice_transaction_line_portal_type)
    self.assertEqual(3, len(accounting_line_list))

    receivable_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.receivable_account]
    self.assertEqual(1, len(receivable_movement_list))
    receivable_movement = receivable_movement_list[0]
    self.assertEqual(receivable_movement.getDestinationValue(),
                      self.payable_account)
    self.assertEqual(1150, receivable_movement.getSourceDebit())

    collected_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.collected_tax_account]
    self.assertEqual(1, len(collected_movement_list))
    collected_movement = collected_movement_list[0]
    self.assertEqual(collected_movement.getDestinationValue(),
                      self.refundable_tax_account)
    self.assertEqual(150, collected_movement.getSourceCredit())

    income_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.income_account]
    self.assertEqual(1, len(income_movement_list))
    income_movement = income_movement_list[0]
    self.assertEqual(income_movement.getDestinationValue(),
                      self.expense_account)
    self.assertEqual(1000, income_movement.getSourceCredit())

  def test_BuildTradeModelLineAndAccountingFromInvoice(self):
    business_process = self.createBusinessProcess()

    product = self.createProductTaxed()
    tax = self.createServiceTax()
    currency = self.createResource('Currency', title='EUR')
    trade_condition = self.createTradeCondition(
      business_process, (
      dict(reference='VAT',
           price=.15,
           resource_value=tax,
           trade_phase='trade/tax',
           base_application='base_amount/tax'),
      ))
    source = self.createNode()
    destination = self.createNode()

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
    self.tic()

    self.assertEqual(2, len(invoice.getMovementList()))
    self.assertEqual(1150, invoice.getTotalPrice())
    self.assertEqual([], invoice.getDivergenceList())

    invoice.start()
    self.tic()

    self.assertEqual([], invoice.getDivergenceList())
    accounting_line_list = invoice.getMovementList(
             portal_type=self.invoice_transaction_line_portal_type)
    self.assertEqual(3, len(accounting_line_list))

    receivable_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.receivable_account]
    self.assertEqual(1, len(receivable_movement_list))
    receivable_movement = receivable_movement_list[0]
    self.assertEqual(receivable_movement.getDestinationValue(),
                      self.payable_account)
    self.assertEqual(1150, receivable_movement.getSourceDebit())

    collected_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.collected_tax_account]
    self.assertEqual(1, len(collected_movement_list))
    collected_movement = collected_movement_list[0]
    self.assertEqual(collected_movement.getDestinationValue(),
                      self.refundable_tax_account)
    self.assertEqual(150, collected_movement.getSourceCredit())

    income_movement_list = [m for m in accounting_line_list if
        m.getSourceValue() == self.income_account]
    self.assertEqual(1, len(income_movement_list))
    income_movement = income_movement_list[0]
    self.assertEqual(income_movement.getDestinationValue(),
                      self.expense_account)
    self.assertEqual(1000, income_movement.getSourceCredit())

  def test_tradeModelLineWithTargetLevelSetting(self):
    """
      Test that target level setting can specify a target of trade model line
      and trade model line can works with appropriate context(delivery or
      movement) only.
    """
    bounded_fee = self.setBaseAmountQuantityMethod('bounded_fee', """\
return lambda *args, **kw: min(800,
  context.getBaseAmountQuantity(*args, **kw))""")
    fixed_quantity = self.setBaseAmountQuantityMethod('fixed_quantity', """\
return lambda *args, **kw: 1""")

    tax = self.createServiceTax()
    trade_condition = self.createTradeCondition(self.createBusinessProcess())
    # create a model line and set target level to `delivery`.
    tml = self.createTradeModelLine(trade_condition,
                                    reference='TAX',
                                    resource_value=tax,
                                    base_application='base_amount/tax',
                                    target_delivery=True,
                                    price=0.05)

    # create an order.
    resource_A = self.createResource('Product', title='A')
    resource_B = self.createResource('Product', title='B')
    order = self.createOrder(trade_condition)
    base_contribution_list = 'base_amount/tax', bounded_fee
    kw = {'portal_type': self.order_line_portal_type,
          'base_contribution_list': base_contribution_list}
    order.newContent(price=1000, quantity=1,
                     resource_value=resource_A, **kw)
    order.newContent(price=500, quantity=1,
                     resource_value=resource_B, **kw)
    amount_list = order.getGeneratedAmountList()
    self.assertEqual([75], [x.getTotalPrice() for x in amount_list])

    # change target level to `movement`.
    tml.setTargetDelivery(False)
    amount_list = order.getGeneratedAmountList()
    self.assertEqual([25, 50], sorted(x.getTotalPrice() for x in amount_list))

    # create other trade model lines.
    # for movement
    extra_fee_a = self.createTradeModelLine(trade_condition,
                                            reference='EXTRA_FEE_A',
                                            resource_value=tax,
                                            base_application=bounded_fee,
                                            price=.2)
    # Extra fee b has a fixed quantity so that this trade model line is applied
    # to all movements by force.
    extra_fee_b = self.createTradeModelLine(trade_condition,
                                            reference='EXTRA_FEE_B',
                                            resource_value=tax,
                                            base_application=fixed_quantity,
                                            price=1)
    # for delivery level
    self.createTradeModelLine(trade_condition,
                              reference='DISCOUNT_B',
                              resource_value=tax,
                              base_application=fixed_quantity,
                              target_delivery=True,
                              quantity=10, price=-1)

    self.commit()# flush transactional cache

    expected_tax = 1000*0.05, 500*0.05, 500*0.2, 800*0.2, 1, 1, -10
    amount_list = order.getGeneratedAmountList()
    self.assertEqual(sorted(expected_tax),
                     sorted(x.getTotalPrice() for x in amount_list))
    amount_list = order.getAggregatedAmountList()
    expected_tax = 1000*0.05 + 500*0.05, 500*0.2 + 800*0.2, 1 + 1, -10
    self.assertEqual(sorted(expected_tax),
                     sorted(x.getTotalPrice() for x in amount_list))
    # Change target level
    extra_fee_a.setTargetDelivery(True)
    extra_fee_b.setTargetDelivery(True)
    amount_list = order.getAggregatedAmountList()
    expected_tax = 1000*0.05 + 500*0.05, 800*0.2, 1, -10
    self.assertEqual(sorted(expected_tax),
                     sorted(x.getTotalPrice() for x in amount_list))

  @expectedFailure
  def test_tradeModelLineWithRounding(self):
    """
      Test if trade model line works with rounding.
    """
    trade_condition = self.createTradeCondition(self.createBusinessProcess())
    # create a model line and set target level to `delivery`
    tax = self.createTradeModelLine(trade_condition,
                                    reference='TAX',
                                    base_application='base_amount/tax',
                                    base_contribution='base_amount/total_tax',
                                    price=0.05,
                                    target_delivery=True)

    # create a rounding model for tax
    rounding_model = self.portal.portal_roundings.newContent(portal_type='Rounding Model')
    rounding_model.setDecimalRoundingOption('ROUND_DOWN')
    rounding_model.setPrecision(1)
    rounding_model.setRoundedPropertyId('total_price')
    rounding_model._setMembershipCriterionCategoryList(['base_contribution/base_amount/total_tax'])
    rounding_model._setMembershipCriterionBaseCategoryList(['base_contribution'])
    rounding_model.validate()

    # create an order
    resource_A = self.createResource('Product', title='A')
    resource_B = self.createResource('Product', title='B')
    order = self.createOrder(trade_condition)
    order_line_1 = order.newContent(portal_type=self.order_line_portal_type,
                                    price=3333, quantity=1,
                                    resource_value=resource_A,
                                    base_contribution='base_amount/tax')
    order_line_2 = order.newContent(portal_type=self.order_line_portal_type,
                                    price=171, quantity=1,
                                    resource_value=resource_B,
                                    base_contribution='base_amount/tax')

    self.tic()
    # check the result without rounding
    amount, = order.getAggregatedAmountList(rounding=False)
    self.assertEqual((3333+171)*0.05, amount.getTotalPrice()) # 175.2
    # check the result with rounding
    amount, = order.getAggregatedAmountList(rounding=True)
    self.assertEqual(175, amount.getTotalPrice())

    # change tax trade model line to `movement` level
    tax.setTargetDelivery(False)

    def getTotalAmount(amount_list):
      result = 0
      for amount in amount_list:
        if amount.getBaseContribution() in ('base_amount/total',
                                            'base_amount/total_tax'):
          result += amount.getTotalPrice()
      return result

    # check the result without rounding
    amount, = order.getAggregatedAmountList(rounding=False)
    self.assertEqual(3333*0.05+171*0.05, amount.getTotalPrice()) # 175.2
    # check the result with rounding
    amount_list = order.getAggregatedAmountList(rounding=True)
    # XXX Here, the assertion will fail with the current implementation.
    self.assertEqual(2, len(amount_list)) # XXX 1 or 2 ???
    # XXX and here, the result is 175, because round is applied against
    # already aggregated single amount.
    self.assertEqual(174, getTotalAmount(amount_list))

    # check getAggregatedAmountList result of each movement
    # order line 1
    amount, = order_line_1.getAggregatedAmountList(rounding=False)
    self.assertEqual(3333*0.05, amount.getTotalPrice()) # 166.65
    amount, = order_line_1.getAggregatedAmountList(rounding=True)
    self.assertEqual(166, amount.getTotalPrice())
    # order line 2
    amount, = order_line_2.getAggregatedAmountList(rounding=False)
    self.assertEqual(171*0.05, amount.getTotalPrice()) # 8.55
    amount, = order_line_2.getAggregatedAmountList(rounding=True)
    self.assertEqual(8, amount.getTotalPrice())

    # change rounding model definition
    rounding_model.setDecimalRoundingOption('ROUND_UP')
    rounding_model.setPrecision(1)
    rounding_model.setRoundedPropertyIdList(['total_price', 'quantity'])

    # change quantity
    order_line_1.edit(quantity=3.3333)

    self.tic()

    # check the result without rounding
    amount, = order.getAggregatedAmountList(rounding=False)
    self.assertEqual(3.3333*3333*0.05+171*0.05, amount.getTotalPrice())
    # check the result with rounding
    # both quantity and total price will be rounded so that the expression
    # should be "round_up(round_up(3.3333 * 3333) * 0.05) + round_up(round_up
    # (1* 171) * 0.05)"
    amount_list = order.getAggregatedAmountList(rounding=True)
    self.assertEqual(2, len(amount_list)) # XXX 1 or 2 ???
    self.assertEqual(565, getTotalAmount(amount_list))

    # create a rounding model to round quantity property of order line
    rounding_model_for_quantity = self.portal.portal_roundings.newContent(portal_type='Rounding Model')
    rounding_model_for_quantity.setDecimalRoundingOption('ROUND_DOWN')
    rounding_model_for_quantity.setPrecision(1)
    rounding_model_for_quantity.setRoundedPropertyId('quantity')
    rounding_model_for_quantity._setMembershipCriterionCategoryList(['base_contribution/base_amount/tax'])
    rounding_model_for_quantity._setMembershipCriterionBaseCategoryList(['base_contribution'])
    rounding_model_for_quantity.validate()

    self.tic()

    amount_list = order.getAggregatedAmountList(rounding=True)
    # The expression should be "round_up(round_up(round_down(3.3333) * 3333)
    # * 0.05) + round_up(round_up(round_down(1) * 171) * 0.05)"
    self.assertEqual(2, len(amount_list)) # XXX 1 or 2 ???
    self.assertEqual(509, getTotalAmount(amount_list))

    # create a rounding model to round price property of order line
    rounding_model_for_price = self.portal.portal_roundings.newContent(portal_type='Rounding Model')
    rounding_model_for_price.setDecimalRoundingOption('ROUND_UP')
    rounding_model_for_price.setPrecision(0.1)
    rounding_model_for_price.setRoundedPropertyId('price')
    rounding_model_for_price._setMembershipCriterionCategoryList(['base_contribution/base_amount/tax'])
    rounding_model_for_price._setMembershipCriterionBaseCategoryList(['base_contribution'])
    rounding_model_for_price.validate()

    # change price
    order_line_2.edit(price=171.1234)
    # invalidate rounding model for total price
    rounding_model.invalidate()

    self.tic()

    # check the result without rounding
    amount, = order.getAggregatedAmountList(rounding=False)
    self.assertEqual(3.3333*3333*0.05+171.1234*0.05, amount.getTotalPrice())
    # check the result with rounding
    amount_list = order.getAggregatedAmountList(rounding=True)
    # The expression should be "round_down(3.3333) * round_up(3333) * 0.05 +
    # round_down(1) * round_up(171.1234) * 0.05"
    self.assertEqual(2, len(amount_list)) # XXX 1 or 2 ???
    self.assertEqual(508.51000000000005, getTotalAmount(amount_list))

  def test_tradeModelLineWithEmptyBaseContributionMovement(self):
    """
    Make sure that a movement which does not have any base_contribution values
    does not match to any trade model lines.
    """
    trade_condition = self.createTradeCondition(
      (), (
      dict(price=0.05,
           reference='TAX',
           base_application_list=['base_amount/tax'],
           base_contribution_list=['base_amount/total_tax']),
      ))

    # create an order
    resource_A = self.createResource('Product', title='A')
    order = self.createOrder(
      trade_condition, (
      # create a movement which should be aggregated
      dict(id='1',
           price=100, quantity=1,
           resource_value=resource_A,
           base_contribution_list=['base_amount/tax']),
      # create a movement which base contribution is empty and shoud not be
      # aggregated
      dict(id='2',
           price=31, quantity=1,
           resource_value=resource_A,
           base_contribution_list=[]),
      ))

    self.tic()

    # check the result
    amount, = order.getAggregatedAmountList()
    self.assertEqual(100*0.05, amount.getTotalPrice())


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
