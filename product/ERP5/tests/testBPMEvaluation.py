# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
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
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################
"""
This is BPM Evaluation Test class using erp5_bpm development Business Template

Generally it tries to use two Business Processes - one with sequence very
similar to normal ERP5 - TestBPMEvaluationDefaultProcessMixin, second one
inverted - TestBPMEvaluationDifferentProcessMixin.

It uses only Sale path to demonstrate BPM.

It is advised to *NOT* remove erp5_administration.
"""
import unittest
import transaction

from Products.ERP5.tests.testBPMCore import TestBPMMixin

from DateTime import DateTime

class TestBPMEvaluationMixin(TestBPMMixin):
  node_portal_type = 'Organisation'
  order_portal_type = 'Sale Order'
  order_line_portal_type = 'Sale Order Line'
  packing_list_portal_type = 'Sale Packing List'
  packing_list_line_portal_type = 'Sale Packing List Line'
  trade_condition_portal_type = 'Sale Trade Condition'
  invoice_portal_type = 'Sale Invoice Transaction'
  product_portal_type = 'Product'
  order_start_date = DateTime()
  order_stop_date = order_start_date + 10

  def getBusinessTemplateList(self):
    return TestBPMMixin.getBusinessTemplateList(self) + ('erp5_bpm',
        'erp5_administration', 'erp5_simulation',)

  def afterSetUp(self):
    TestBPMMixin.afterSetUp(self)
    self._createNodes()
    self._createBusinessProcess()
    self._createTradeCondition()
    self._createRootDocument()
    self._setUpRules()
    self.stepTic()

  def _setUpRules(self):
    """Setups rules

    Rules are part of configuration, so anything provided by Business
    Templates or previous test runs is ignored - all old rules are invalidated
    between tests and new rules are created, configured and validated.
    """
    self.rule_tool = self.portal.portal_rules
    for rule in self.rule_tool.contentValues():
      if rule.getValidationState() == 'validated':
        rule.invalidate()
    transaction.commit()
    self._createOrderRootSimulationRule()
    self._createDeliveryRootSimulationRule()
    self._createDeliverySimulationRule()
    self._createInvoiceSimulationRule()
    self._createInvoiceRootSimulationRule()
    self._createTradeModelSimulationRule()

  def _createTradeRootSimulationRule(self, **kw):
    edit_dict = {}
    edit_dict.update(
      trade_phase = 'default/delivery',
    )
    edit_dict.update(**kw)
    rule = self.rule_tool.newContent(**edit_dict)

    # matching providers
    for category in ('delivery',):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)

    # divergence providers
    for category in ('source_section',
                     'resource',
                     'destination_section',
                     'source',
                     'aggregate'):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    return rule

  def _createOrderRootSimulationRule(self):
    rule = self._createTradeRootSimulationRule(portal_type='Order Root Simulation Rule',
        trade_phase='default/order',                                       
        reference='default_order_rule')
    rule.validate()
    transaction.commit()

  def _createDeliveryRootSimulationRule(self):
    rule = self._createTradeRootSimulationRule(portal_type='Delivery Root Simulation Rule',
        reference='default_delivery_rule')
    rule.validate()
    transaction.commit()

  def _createDeliverySimulationRule(self):
    rule = self.rule_tool.newContent(portal_type='Delivery Simulation Rule',
      reference='default_delivering_rule',
      trade_phase='default/delivery',
      test_method_id = ('SimulationMovement_testDeliverySimulationRule',)
      )
    # matching providers
    for category in ('resource',):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    rule.newContent(
      portal_type='Variation Divergence Tester',
      title='variation divergence tester',
      tested_property='variation_property_dict',
      divergence_provider=False,
      matching_provider=True)

    # divergence providers
    for category in ('resource',
                     'source_section',
                     'destination_section',
                     'source',
                     'source_function',
                     'destination',
                     'destination_function',
                     'source_project',
                     'destination_project',
                     'aggregate',
                     'price_currency',
                     'base_contribution',
                     'base_application',
                     'source_account',
                     'destination_account',
                     ):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    rule.validate()
    transaction.commit()

  def _createTradeModelSimulationRule(self):
    rule = self.rule_tool.newContent(portal_type='Trade Model Simulation Rule',
      reference='default_trade_model_rule',
      test_method_id = ('SimulationMovement_testTradeModelSimulationRule',)
      )
    # matching providers
    for category in ('resource',):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    rule.newContent(
      portal_type='Variation Divergence Tester',
      title='variation divergence tester',
      tested_property='variation_property_dict',
      divergence_provider=False,
      matching_provider=True)

    # divergence providers
    for category in ('resource',
                     'source_section',
                     'destination_section',
                     'source',
                     'source_function',
                     'destination_function',
                     'source_project',
                     'destination_project',
                     'aggregate',
                     'price_currency',
                     'base_contribution',
                     'base_application',
                     'source_account',
                     'destination_account',
                     ):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    rule.validate()
    transaction.commit()

  def _createInvoiceRootSimulationRule(self):
    # Note: This is not used, but invoices, even if built from simulation,
    #       need those rule to create empty one applied rule
    rule_tool = self.portal.portal_rules

    clipboard = rule_tool.manage_copyObjects(ids = ['new_invoice_root_simulation_rule'])
    pasted = rule_tool.manage_pasteObjects(clipboard)
    new_rule = getattr(rule_tool, pasted[0]['new_id'])
    new_rule.validate()
    transaction.commit()

  def _createInvoiceSimulationRule(self):
    edit_dict = {}
    edit_dict.update(
    )
    rule = self.rule_tool.newContent(portal_type='Invoice Simulation Rule',
      reference='default_invoicing_rule',
      trade_phase = 'default/invoicing',
      test_method_id = ('SimulationMovement_testInvoiceSimulationRule',)
      )
    # matching providers
    for category in ('resource',):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=False,
        matching_provider=True)
    rule.newContent(
      portal_type='Variation Divergence Tester',
      title='variation divergence tester',
      tested_property='variation_property_dict',
      divergence_provider=False,
      matching_provider=True)

    # divergence providers
    for category in ('resource',
                     'source_section',
                     'destination_section',
                     'source',
                     'source_function',
                     'destination_function',
                     'source_project',
                     'destination_project',
                     'aggregate',
                     'price_currency',
                     'base_contribution',
                     'base_application',
                     'source_account',
                     'destination_account',
                     ):
      rule.newContent(
        portal_type='Category Membership Divergence Tester',
        title='%s divergence tester' % category,
        tested_property=category,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Net Converted Quantity Divergence Tester',
      title='quantity divergence tester',
      tested_property='quantity',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)
    for property_id in ('start_date', 'stop_date'):
      rule.newContent(
        portal_type='DateTime Divergence Tester',
        title='%s divergence tester' % property_id,
        tested_property=property_id,
        quantity=0,
        divergence_provider=True,
        matching_provider=False)
    rule.newContent(
      portal_type='Float Divergence Tester',
      title='price divergence tester',
      tested_property='price',
      quantity=0,
      divergence_provider=True,
      matching_provider=False)

    rule.validate()
    transaction.commit()

  def _createDocument(self, portal_type, **kw):
    module = self.portal.getDefaultModule(portal_type=portal_type)
    return module.newContent(portal_type=portal_type, **kw)

  def _createProduct(self, **kw):
    return self._createDocument(self.product_portal_type, **kw)

  def _createNode(self, **kw):
    return self._createDocument(self.node_portal_type, **kw)

  def _createTradeCondition(self, **kw):
    self.trade_condition = self._createDocument(
        self.trade_condition_portal_type,
        title = self.id(),
        specialise_value=self.business_process, **kw)

  def _createRootDocumentLine(self, **kw):
    return self.root_document.newContent(
        portal_type=self.root_document_line_portal_type, **kw)

  def _createNodes(self):
    self.source, self.source_section = self._createNode(), self._createNode()
    self.destination, self.destination_section = self._createNode() \
        , self._createNode()

  def _setTradeStateList(self):
    """Creates list of defaults states, set them on self as name_state property"""
    tool = self.getCategoryTool()
    for state_name in ('ordered', 'delivered', 'invoiced', 'accounted',
        'paid'):
      setattr(self,'%s_state' % state_name, tool.trade_state._getOb(state_name))

  def _createRootDocument(self):
    self.root_document = self._createDocument(self.root_document_portal_type,
        source_value = self.source,
        source_section_value = self.source_section,
        destination_value = self.destination,
        destination_section_value = self.destination_section,
        start_date = self.order_start_date,
        stop_date = self.order_stop_date,
        specialise_value = self.trade_condition)

  def _checkBPMSimulation(self):
    """Checks BPMised related simumation.

    Note: Simulation tree is the same, it is totally independent from
    BPM sequence"""
    # TODO:
    #  - gather errors into one list
    bpm_root_rule = self.root_document.getCausalityRelatedValue(
        portal_type='Applied Rule')
    # check that correct root rule applied
    self.assertEqual(bpm_root_rule.getSpecialiseValue().getPortalType(),
        self.root_rule_portal_type)
    root_simulation_movement_list = bpm_root_rule.contentValues()
    for root_simulation_movement in root_simulation_movement_list:
      self.assertEqual(root_simulation_movement.getPortalType(),
          'Simulation Movement')
      movement = root_simulation_movement.getDeliveryValue()
      property_problem_list = []
      # check some properties equality between delivery line and simulation
      # movement, gather errors
      for property in 'resource', 'price', 'start_date', 'stop_date', \
                      'source', 'destination', 'source_section', \
                      'destination_section':
        if movement.getProperty(property) != root_simulation_movement \
            .getProperty(property):
          property_problem_list.append('property %s movement %s '
              'simulation %s' % (property, movement.getProperty(property),
                root_simulation_movement.getProperty(property)))
      if len(property_problem_list) > 0:
        self.fail('\n'.join(property_problem_list))
      self.assertEqual(
        movement.getQuantity() * root_simulation_movement.getDeliveryRatio(),
        root_simulation_movement.getQuantity())
      # root rule is order or delivery - so below each movement invoicing one
      # is expected
      self.assertEquals(len(root_simulation_movement.contentValues()), 1)
      if self.root_rule_portal_type == 'Order Root Simulation Rule':
        delivery_rule = root_simulation_movement.contentValues()[0]
        delivery_simulation_movement_list = delivery_rule.contentValues()
        self.assertEqual(1, len(delivery_simulation_movement_list))
        delivery_simulation_movement = delivery_simulation_movement_list[0]
      else:
        delivery_simulation_movement = root_simulation_movement
      for bpm_invoicing_rule in delivery_simulation_movement.contentValues():
        self.assertEqual(bpm_invoicing_rule.getPortalType(), 'Applied Rule')
        self.assertEqual(bpm_invoicing_rule.getSpecialiseValue() \
            .getPortalType(), 'Invoice Simulation Rule')
        # only one movement inside invoicing rule
        self.assertEquals(len(bpm_invoicing_rule.contentValues()), 1)
        for invoicing_simulation_movement in bpm_invoicing_rule \
            .contentValues():
          self.assertEqual(invoicing_simulation_movement.getPortalType(),
              'Simulation Movement')
          self.assertEqual(invoicing_simulation_movement.getCausalityValue(),
              self.invoice_path)
          property_problem_list = []
          # check equality of some properties, gather them
          for property in 'resource', 'price', 'start_date', \
            'stop_date', 'source', 'destination', 'source_section', \
            'destination_section':
            if movement.getProperty(property) != \
                invoicing_simulation_movement.getProperty(property):
              property_problem_list.append('property %s movement %s '
                  'simulation %s' % (property, movement.getProperty(property),
                    invoicing_simulation_movement.getProperty(property)))
          if len(property_problem_list) > 0:
            self.fail('\n'.join(property_problem_list))
          self.assertEqual(
            movement.getQuantity() * root_simulation_movement.getDeliveryRatio(),
            invoicing_simulation_movement.getQuantity())
          # simple check for trade model rule existence, without movements,
          # as no trade condition configured
          self.assertEquals(
              len(invoicing_simulation_movement.contentValues()), 1)
          for trade_model_rule in invoicing_simulation_movement \
              .contentValues():
            self.assertEqual(trade_model_rule.getPortalType(), 'Applied Rule')
            self.assertEqual(trade_model_rule.getSpecialiseValue() \
                .getPortalType(), 'Trade Model Simulation Rule')
            self.assertSameSet(trade_model_rule.contentValues(
              portal_type='Simulation Movement'), [])

class TestBPMEvaluationDefaultProcessMixin:
  def _createBusinessProcess(self):
    self.business_process = self.createBusinessProcess(title=self.id(),
        referential_date='start_date')
    self._setTradeStateList()

    self.order_path = self.createBusinessLink(self.business_process,
        successor_value=self.ordered_state,
        trade_phase='default/order',
        deliverable=1,
        completed_state_list=['confirmed'],
        frozen_state_list=['confirmed'],
        )

    self.delivery_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.ordered_state,
        successor_value=self.delivered_state,
        trade_phase='default/delivery',
        deliverable=1,
        completed_state_list=['started', 'stopped', 'delivered'],
        frozen_state_list=['started', 'stopped', 'delivered'],
        delivery_builder='portal_deliveries/bpm_sale_packing_list_builder',
        )

    self.invoice_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.delivered_state,
        successor_value=self.invoiced_state,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'],
        delivery_builder='portal_deliveries/bpm_sale_invoice_builder',
        trade_phase='default/invoicing')

    self.account_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.invoiced_state,
        successor_value=self.accounted_state,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'],
        trade_phase='default/accounting')

    self.pay_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.invoiced_state,
        successor_value=self.accounted_state,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'],
        trade_phase='default/payment')

    self.stepTic()

class TestBPMEvaluationDifferentProcessMixin:
  def _createBusinessProcess(self):
    self.business_process = self.createBusinessProcess(title=self.id(),
        referential_date='start_date')
    self._setTradeStateList()

    self.order_path = self.createBusinessLink(self.business_process,
        successor_value=self.ordered_state,
        trade_phase='default/order',
        deliverable=1,
        completed_state_list=['confirmed'],
        frozen_state_list=['confirmed'],
        )

    self.invoice_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.ordered_state,
        successor_value=self.invoiced_state,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'],
        trade_phase='default/invoicing')

    self.account_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.invoiced_state,
        successor_value=self.accounted_state,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'],
        trade_phase='default/accounting')

    self.pay_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.accounted_state,
        successor_value=self.paid_state,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'],
        trade_phase='default/payment')

    self.delivery_path = self.createBusinessLink(self.business_process,
        predecessor_value=self.paid_state,
        successor_value=self.delivered_state,
        trade_phase='default/delivery',
        deliverable=1,
        completed_state_list=['delivered'],
        frozen_state_list=['stopped', 'delivered'])

    self.stepTic()

class GenericRuleTestsMixin:
  """Tests which are generic for BPMised Order, Delivery and Invoice Rule"""
  def test_transition(self):
    self.order_line = self._createRootDocumentLine(
      resource_value = self._createProduct(), quantity = 10, price = 5)
    self.stepTic()

    self._doFirstTransition(self.root_document)
    self.stepTic()
    self._checkBPMSimulation()

  def _split(self):
    """Invoke manual splitting"""
    ratio = .5 # hardcoded value, hopefully float friendly
    applied_rule = self.root_document.getCausalityRelatedValue(
        portal_type='Applied Rule')
    for movement in applied_rule.contentValues(
        portal_type='Simulation Movement'):
      new_movement = movement.Base_createCloneDocument(batch_mode=1)
      old_quantity = movement.getQuantity()
      movement.edit(
        quantity = old_quantity * ratio
      )

      new_movement.edit(
        quantity = old_quantity * (1 - ratio)
      )

    self.stepTic()

    # recalculate order ratio
    for movement in self.root_document.getMovementList():
      movement_quantity = movement.getQuantity()
      for simulation_movement in movement.getDeliveryRelatedValueList():
        new_ratio = simulation_movement.getQuantity() / movement_quantity
        simulation_movement.edit(order_ratio = new_ratio)
        if simulation_movement.getDelivery() is not None:
          simulation_movement.edit(delivery_ratio = new_ratio)

    # reexpand
    applied_rule.expand()
    self.stepTic()

    self._checkBPMSimulation()

  def test_transition_split(self):
    self.order_line = self._createRootDocumentLine(
      resource_value = self._createProduct(), quantity = 10, price = 5)
    self.stepTic()

    self._doFirstTransition(self.root_document)
    self.stepTic()
    self._checkBPMSimulation()

    self._split()

    # expand
    self.root_document.edit(title = self.root_document.getTitle() + 'a')

    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_split_line_add(self):
    self.test_transition_split()
    self.order_line_2 = self._createRootDocumentLine(
        resource_value = self._createProduct(), quantity = 4, price = 2)
    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_split_line_add_split(self):
    self.test_transition_split_line_add()

    # second split
    self._split()

    # expand
    self.root_document.edit(title = self.root_document.getTitle() + 'a')

    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_line_edit(self):
    self.test_transition()
    self.order_line.edit(quantity = 8, price = 6)
    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_line_edit_add(self):
    self.test_transition_line_edit()
    self.order_line_2 = self._createRootDocumentLine(
        resource_value = self._createProduct(), quantity = 4, price = 2)
    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_line_edit_add_many_transactions(self):
    self.test_transition_line_edit()
    self.order_line_9 = self._createRootDocumentLine()
    self.stepTic()
    self._checkBPMSimulation()

    self.order_line_9.edit(resource_value = self._createProduct())
    self.stepTic()
    self._checkBPMSimulation()

    self.order_line_9.edit(quantity = 1)
    self.stepTic()
    self._checkBPMSimulation()

    self.order_line_9.edit(price = 33)
    self.stepTic()
    self._checkBPMSimulation()

    self.order_line_9.edit(resource_value = self._createProduct())
    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_line_edit_add_same_resource(self):
    self.test_transition_line_edit()
    resource = self.order_line.getResourceValue()
    self.order_line_10 = self._createRootDocumentLine(
      resource_value = resource, quantity = 9, price = 2)
    self.stepTic()
    self._checkBPMSimulation()

  def test_transition_line_edit_add_same_resource_edit_again(self):
    self.test_transition_line_edit_add_same_resource()

    self.root_document.edit(title = self.root_document.getTitle() + 'a' )
    self.stepTic()
    self._checkBPMSimulation()

class TestOrder(TestBPMEvaluationMixin, GenericRuleTestsMixin):
  """Check BPMised Order Rule behaviour"""
  root_document_portal_type = 'Sale Order'
  root_document_line_portal_type = 'Sale Order Line'
  root_rule_portal_type = 'Order Root Simulation Rule'

  def _doFirstTransition(self, document):
    document.plan()

  def test_confirming(self):
    self.order_line = self._createRootDocumentLine(
      resource_value = self._createProduct(), quantity = 10, price = 5)
    self.stepTic()

    self.root_document.confirm()
    self.stepTic()
    self._checkBPMSimulation()
    self.assertEqual(
      2,
      len(self.root_document.getCausalityRelatedList())
    )
    self.assertEqual(
      'Applied Rule',
      self.root_document.getCausalityRelatedValue(
        portal_type='Applied Rule').getPortalType()
    )

    self.assertEqual(
      self.packing_list_portal_type,
      self.root_document.getCausalityRelatedValue(
        portal_type=self.packing_list_portal_type).getPortalType()
    )

class TestPackingList(TestBPMEvaluationMixin, GenericRuleTestsMixin):
  """Check BPM Delivery Rule behaviour"""
  root_document_portal_type = 'Sale Packing List'
  root_document_line_portal_type = 'Sale Packing List Line'
  root_rule_portal_type = 'Delivery Root Simulation Rule'

  def _packDelivery(self):
    """Packs delivery fully, removes possible containers before"""
    self.root_document.deleteContent(self.root_document.contentIds(
      filter={'portal_type':'Container'}))
    cont = self.root_document.newContent(portal_type='Container')
    for movement in self.root_document.getMovementList():
      cont.newContent(portal_type='Container Line',
        resource = movement.getResource(), quantity = movement.getQuantity())
    self.stepTic()
    self._checkBPMSimulation()

  def _doFirstTransition(self, document):
    document.confirm()

  def test_starting(self):
    self.delivery_line = self._createRootDocumentLine(
      resource_value = self._createProduct(), quantity = 10, price = 5)
    self.stepTic()

    self.root_document.confirm()
    self.stepTic()
    self._checkBPMSimulation()

    self._packDelivery()

    self.root_document.start()
    self.stepTic()
    self._checkBPMSimulation()

    self.assertEqual(
      2,
      len(self.root_document.getCausalityRelatedList())
    )
    self.assertEqual(
      'Applied Rule',
      self.root_document.getCausalityRelatedValue(
        portal_type='Applied Rule').getPortalType()
    )

    self.assertEqual(
      self.invoice_portal_type,
      self.root_document.getCausalityRelatedValue(
        portal_type=self.invoice_portal_type).getPortalType()
    )

class TestInvoice(TestBPMEvaluationMixin, GenericRuleTestsMixin):
  """Check BPM Invoice Rule behaviour"""
  # not implemented yet
  pass

class TestOrderDefaultProcess(TestOrder,
    TestBPMEvaluationDefaultProcessMixin):
  pass

class TestPackingListDefaultProcess(TestPackingList,
    TestBPMEvaluationDefaultProcessMixin):
  pass

class TestInvoiceDefaultProcess(TestInvoice,
    TestBPMEvaluationDefaultProcessMixin):
  pass

class TestOrderDifferentProcess(TestOrder,
    TestBPMEvaluationDifferentProcessMixin):
  def test_confirming(self):
    # in current BPM configuration nothing shall be built
    # as soon as test business process will be finished, it shall built proper
    # delivery
    self.order_line = self._createRootDocumentLine(
      resource_value = self._createProduct(), quantity = 10, price = 5)
    self.stepTic()

    self.root_document.confirm()
    self.stepTic()
    self._checkBPMSimulation()
    self.assertEqual(
      1,
      len(self.root_document.getCausalityRelatedList())
    )
    self.assertEqual(
      'Applied Rule',
      self.root_document.getCausalityRelatedValue().getPortalType()
    )

class TestPackingListDifferentProcess(TestPackingList,
    TestBPMEvaluationDifferentProcessMixin):
  def test_starting(self):
    self.delivery_line = self._createRootDocumentLine(
      resource_value = self._createProduct(), quantity = 10, price = 5)
    self.stepTic()

    self.root_document.confirm()
    self.stepTic()
    self._checkBPMSimulation()

    self._packDelivery()
    self.root_document.start()
    self.stepTic()
    self._checkBPMSimulation()

    self.assertEqual(
      1,
      len(self.root_document.getCausalityRelatedList())
    )
    self.assertEqual(
      'Applied Rule',
      self.root_document.getCausalityRelatedValue(
        portal_type='Applied Rule').getPortalType()
    )

class TestInvoiceDifferentProcess(TestInvoice,
    TestBPMEvaluationDifferentProcessMixin):
  pass

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOrderDefaultProcess))
  suite.addTest(unittest.makeSuite(TestPackingListDefaultProcess))
#  suite.addTest(unittest.makeSuite(TestInvoiceDefaultProcess))

  suite.addTest(unittest.makeSuite(TestOrderDifferentProcess))
  suite.addTest(unittest.makeSuite(TestPackingListDifferentProcess))
#  suite.addTest(unittest.makeSuite(TestInvoiceDifferentProcess))
  return suite
