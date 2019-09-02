# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <luke@nexedi.com>
#          Yusuke Muraoka <yusuke@nexedi.com>
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

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from DateTime import DateTime
from Products.ERP5Type.tests.utils import reindex
from Products.ERP5Type.tests.utils import todo_erp5

class TestBPMMixin(ERP5TypeTestCase):
  """Skeletons for tests which depend on BPM"""

  def getBusinessTemplateList(self):
    return ('erp5_base', 'erp5_pdm', 'erp5_simulation', 'erp5_trade', 'erp5_item',
            'erp5_accounting', 'erp5_invoicing', 'erp5_simplified_invoicing',
            'erp5_core_proxy_field_legacy',
            'erp5_configurator_standard_solver',
            'erp5_configurator_standard_trade_template',
            'erp5_configurator_standard_accounting_template',
            'erp5_configurator_standard_invoicing_template',
            'erp5_simulation_test')

  business_process_portal_type = 'Business Process'
  business_link_portal_type = 'Business Link'
  trade_model_path_portal_type = 'Trade Model Path'
  default_business_process = \
    'business_process_module/erp5_default_business_process'

  normal_resource_use_category_list = ['normal']
  invoicing_resource_use_category_list = ['discount', 'tax']

  def createCategoriesInCategory(self, category, category_id_list):
    for category_id in category_id_list:
      if not category.hasObject(category_id):
        category.newContent(category_id,
          title=category_id.replace('_', ' ').title())

  @reindex
  def createCategories(self):
    category_tool = self.portal.portal_categories
    self.createCategoriesInCategory(category_tool.base_amount, ['discount',
      'tax', 'total_tax', 'total_discount', 'total'])
    self.createCategoriesInCategory(category_tool.use,
        self.normal_resource_use_category_list + \
            self.invoicing_resource_use_category_list)
    self.createCategoriesInCategory(category_tool.trade_phase, ['default',])
    self.createCategoriesInCategory(category_tool.trade_phase.default,
        ['accounting', 'delivery', 'invoicing', 'discount', 'tax', 'payment'])
    self.createCategoriesInCategory(category_tool.trade_state,
        ['ordered', 'invoiced', 'delivered', 'taxed',
         'state_a', 'state_b', 'state_c', 'state_d', 'state_e'])
    self.createCategoriesInCategory(category_tool, ('tax_range', 'tax_share'))
    self.createCategoriesInCategory(category_tool.tax_range,
                                    ('0_200', '200_inf'))
    self.createCategoriesInCategory(category_tool.tax_share, 'AB')

  @reindex
  def createBusinessProcess(self, create_order_to_invoice_path=False, **kw):
    module = self.portal.getDefaultModule(
        portal_type=self.business_process_portal_type,)
    business_process =  module.newContent(
      portal_type=self.business_process_portal_type,
      specialise=self.default_business_process)
    self.business_process = business_process
    business_process._edit(**kw)
    if create_order_to_invoice_path:
      self.createTradeModelPath(self.business_process,
        reference='order_path',
        trade_phase_list=('default/order',))
      self.createTradeModelPath(self.business_process,
        reference='delivery_path',
        trade_phase_list=('default/delivery',),
        trade_date='trade_phase/default/order')
      self.createTradeModelPath(self.business_process,
        reference='invoice_path',
        trade_phase_list=('default/invoicing',),
        trade_date='trade_phase/default/delivery')
    self.createTradeModelPath(business_process,
      reference='default_path',
      trade_phase_list=('default/discount', 'default/tax'),
      trade_date='trade_phase/default/invoicing')
    # A trade model path already exist for root simulation movements
    # (Accounting Transaction Root Simulation Rule).
    # The ones we are creating are for Invoice Transaction Simulation Rule
    # so we add a test on the portal type of the input movement.
    kw = dict(business_process=business_process,
              trade_phase='default/accounting',
              trade_date='trade_phase/default/invoicing',
              membership_criterion_base_category='resource_use',
              criterion_property_dict={'portal_type': 'Simulation Movement'})
    self.createTradeModelPath(reference='acounting_tax1',
      efficiency=-1,
      source_value=self.receivable_account,
      destination_value=self.payable_account,
      membership_criterion_category='resource_use/use/tax',
      **kw)
    self.createTradeModelPath(reference='acounting_tax2',
      efficiency=1,
      source_value=self.collected_tax_account,
      destination_value=self.refundable_tax_account,
      membership_criterion_category='resource_use/use/tax',
      **kw)
    self.createTradeModelPath(reference='acounting_discount1',
      efficiency=-1,
      source_value=self.receivable_account,
      destination_value=self.payable_account,
      membership_criterion_category='resource_use/use/discount',
      **kw)
    self.createTradeModelPath(reference='acounting_discount2',
      efficiency=1,
      source_value=self.income_account,
      destination_value=self.expense_account,
      membership_criterion_category='resource_use/use/discount',
      **kw)
    self.createTradeModelPath(reference='acounting_normal1',
      efficiency=-1,
      source_value=self.receivable_account,
      destination_value=self.payable_account,
      membership_criterion_category='resource_use/use/normal',
      **kw)
    self.createTradeModelPath(reference='acounting_normal2',
      efficiency=1,
      source_value=self.income_account,
      destination_value=self.expense_account,
      membership_criterion_category='resource_use/use/normal',
      **kw)
    return business_process

  @reindex
  def createBusinessLink(self, business_process=None, **kw):
    if business_process is None:
      business_process = self.createBusinessProcess()
    if kw.get('reference'):
      kw.setdefault('id', kw['reference'])
    business_link = business_process.newContent(
      portal_type=self.business_link_portal_type, **kw)
    return business_link

  def createTradeModelPath(self, business_process=None,
                           criterion_property_dict={}, **kw):
    if business_process is None:
      business_process = self.createBusinessProcess()
    if kw.get('reference') and not kw.get('id'):
      kw.setdefault('id', kw['reference'] + '_path')
    trade_model_path = business_process.newContent(
      portal_type=self.trade_model_path_portal_type, **kw)
    if criterion_property_dict:
      trade_model_path._setCriterionPropertyList(tuple(criterion_property_dict))
      for property, identity in criterion_property_dict.iteritems():
        trade_model_path.setCriterion(property, identity)
    reference = kw.get('reference', None)
    if reference is not None:
      setattr(self, reference, trade_model_path)
    return trade_model_path

  def createMovement(self):
    # returns a movement for testing
    applied_rule = self.portal.portal_simulation.newContent(
        portal_type='Applied Rule')
    return applied_rule.newContent(portal_type='Simulation Movement')

  def createAndValidateAccount(self, account_id, account_type):
    account_module = self.portal.account_module
    account = account_module.newContent(portal_type='Account',
          title=account_id,
          account_type=account_type)
    self.assertNotEqual(None, account.getAccountTypeValue())
    account.validate()
    return account

  def createAndValidateAccounts(self):
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

  def afterSetUp(self):
    self.validateRules()
    self.createCategories()
    self.createAndValidateAccounts()
    self.tic()

class TestBPMDummyDeliveryMovementMixin(TestBPMMixin):
  def _createDelivery(self, **kw):
    return self.folder.newContent(portal_type='Dummy Delivery', **kw)

  def _createMovement(self, delivery, **kw):
    return delivery.newContent(portal_type='Dummy Movement', **kw)

  def getBusinessTemplateList(self):
    return super(TestBPMDummyDeliveryMovementMixin, self)\
        .getBusinessTemplateList() \
        + ('erp5_dummy_movement', )

  def afterSetUp(self):
    super(TestBPMDummyDeliveryMovementMixin, self).afterSetUp()
    if not hasattr(self.portal, 'testing_folder'):
      self.portal.newContent(portal_type='Folder',
                            id='testing_folder')
    self.folder = self.portal.testing_folder
    self.tic()

  def beforeTearDown(self):
    super(TestBPMDummyDeliveryMovementMixin, self).beforeTearDown()
    self.portal.deleteContent(id='testing_folder')
    self.tic()

  completed_state = 'delivered'
  frozen_state = 'confirmed'

  completed_state_list = [completed_state]
  frozen_state_list = [completed_state, frozen_state]

  def _createOrderedDeliveredInvoicedBusinessProcess(self):
    # simple business process preparation
    business_process = self.createBusinessProcess(
        create_order_to_invoice_path=True)
    category_tool = self.getCategoryTool()
    ordered = category_tool.trade_state.ordered
    delivered = category_tool.trade_state.delivered
    invoiced = category_tool.trade_state.invoiced

    # path which is completed, as soon as related simulation movements are in
    # proper state
    self.order_link = self.createBusinessLink(business_process,
        successor_value = ordered,
        trade_phase='default/order',
        completed_state_list = self.completed_state_list,
        frozen_state_list = self.frozen_state_list)

    self.delivery_link = self.createBusinessLink(business_process,
        predecessor_value = ordered, successor_value = delivered,
        trade_phase='default/delivery',
        completed_state_list = self.completed_state_list,
        frozen_state_list = self.frozen_state_list)

    self.invoice_link = self.createBusinessLink(business_process,
        predecessor_value = delivered, successor_value = invoiced,
        trade_phase='default/invoicing')
    self.tic()

  def constructSimulationTreeAndDeliveries(self, simulation_depth=None,
               dummy_split=False):
    """
    Construct a simple simulation tree with deliveries. This is
    not real simulation tree, we only need the structure, most
    usual properties are not there (quantities, arrow, etc)

    simulation_depth : level of simulation where we should stop
    """
    # create order and order line to have starting point for business process
    self.order = order = self._createDelivery()
    order_line = self._createMovement(order)

    if simulation_depth is None:
      simulation_depth = float('inf')

    # first level rule with simulation movement
    self.applied_rule = self.portal.portal_simulation.newContent(
        portal_type='Applied Rule', causality_value=order)

    def setTestClassProperty(prefix, property_name, document):
      if prefix:
        property_name = "%s_%s" % (prefix, property_name)
      setattr(self, property_name, document)
      return document

    simulation_movement_kw = {
       'specialise': self.business_process.getRelativeUrl()}
    def constructSimulationTree(applied_rule, prefix=None):
      document = setTestClassProperty(prefix, 'simulation_movement',
        applied_rule.newContent(
        portal_type = 'Simulation Movement',
        delivery_value = order_line,
        trade_phase='default/order',
        causality_value_list=[self.order_link, self.order_path],
        **simulation_movement_kw
        ))

      if simulation_depth > 1:

        # second level rule with simulation movement
        document = setTestClassProperty(prefix, 'delivery_rule',
          document.newContent(
          portal_type='Applied Rule'))
        document = setTestClassProperty(prefix, 'delivery_simulation_movement',
          document.newContent(
          portal_type='Simulation Movement',
          trade_phase='default/delivery',
          causality_value_list=[self.delivery_link, self.delivery_path],
          **simulation_movement_kw))

        if simulation_depth > 2:

          # third level rule with simulation movement
          document = setTestClassProperty(prefix, 'invoicing_rule',
              document.newContent(
              portal_type='Applied Rule'))
          document = setTestClassProperty(prefix,
                        'invoicing_simulation_movement',
              document.newContent(
              portal_type='Simulation Movement',
              trade_phase='default/invoicing',
              causality_value_list=[self.invoice_link, self.invoice_path],
              **simulation_movement_kw))

    constructSimulationTree(self.applied_rule)
    if dummy_split:
      constructSimulationTree(self.applied_rule, prefix='split')
    self.tic()

class TestBPMImplementation(TestBPMDummyDeliveryMovementMixin):
  """Business Process implementation tests"""
  def test_BusinessProcess_getBusinessLinkValueList(self):
    business_process = self.createBusinessProcess()

    accounting_business_link = business_process.newContent(
        portal_type=self.business_link_portal_type,
        trade_phase='default/accounting')

    delivery_business_link = business_process.newContent(
        portal_type=self.business_link_portal_type,
        trade_phase='default/delivery')

    accounting_delivery_business_link = business_process.newContent(
        portal_type=self.business_link_portal_type,
        trade_phase=('default/accounting', 'default/delivery'))

    self.tic()

    self.assertSameSet(
      (accounting_business_link, accounting_delivery_business_link),
      business_process.getBusinessLinkValueList(trade_phase='default/accounting')
    )

    self.assertSameSet(
      (delivery_business_link, accounting_delivery_business_link),
      business_process.getBusinessLinkValueList(trade_phase='default/delivery')
    )

    self.assertSameSet(
      (accounting_delivery_business_link, delivery_business_link,
        accounting_business_link),
      business_process.getBusinessLinkValueList(trade_phase=('default/delivery',
        'default/accounting'))
    )

  def test_BusinessLinkStandardCategoryAccessProvider(self):
    source_node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    source_section_node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    business_link = self.createBusinessLink()
    business_link.setSourceValue(source_node)
    business_link.setSourceSectionValue(source_section_node)
    self.assertEqual([source_node], business_link.getSourceValueList())
    self.assertEqual([source_node.getRelativeUrl()], business_link.getSourceList())
    self.assertEqual(source_node.getRelativeUrl(),
        business_link.getSource(default='something'))

  def test_EmptyBusinessLinkStandardCategoryAccessProvider(self):
    business_link = self.createBusinessLink()
    self.assertEqual(None, business_link.getSourceValue())
    self.assertEqual(None, business_link.getSource())
    self.assertEqual('something',
        business_link.getSource(default='something'))

  def test_BusinessPathDynamicCategoryAccessProvider(self):
    source_node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    source_section_node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    business_path = self.createTradeModelPath()
    business_path.setSourceMethodId('TradeModelPath_getDefaultSourceList')

    context_movement = self.createMovement()
    context_movement.setSourceValue(source_node)
    context_movement.setSourceSectionValue(source_section_node)
    self.assertEqual(None, business_path.getSourceValue())
    self.assertEqual([source_node.getRelativeUrl()],
                      business_path.getArrowCategoryDict(context=context_movement)['source'])

  def test_BusinessPathDynamicCategoryAccessProviderBusinessLinkPrecedence(self):
    movement_node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    path_node = self.portal.organisation_module.newContent(
                    portal_type='Organisation')
    business_path = self.createTradeModelPath()
    business_path.setSourceMethodId('TradeModelPath_getDefaultSourceList')
    business_path.setSourceValue(path_node)

    context_movement = self.createMovement()
    context_movement.setSourceValue(movement_node)
    self.assertEqual(path_node, business_path.getSourceValue())
    self.assertEqual([path_node.getRelativeUrl()],
                      business_path.getArrowCategoryDict(context=context_movement)['source'])

  def test_BusinessPathDynamicCategoryAccessProviderEmptyMovement(self):
    business_path = self.createTradeModelPath()
    business_path.setSourceMethodId('TradeModelPath_getDefaultSourceList')

    context_movement = self.createMovement()
    self.assertEqual(None, business_path.getSourceValue())
    self.assertFalse(business_path.getArrowCategoryDict(context=context_movement).has_key('source'))

  def test_BusinessState_getRemainingTradePhaseList(self):
    """
    This test case is described for what trade_phase is remaining after the
    given business link.
    """
    # define business process
    category_tool = self.getCategoryTool()
    business_process = self.createBusinessProcess()
    business_link_order = self.createBusinessLink(business_process,
                                 title='order', id='order',
                                 trade_phase='default/order')
    business_link_deliver = self.createBusinessLink(business_process,
                                 title='deliver', id='deliver',
                                 trade_phase='default/delivery')
    business_link_invoice = self.createBusinessLink(business_process,
                                 title='invoice', id='invoice',
                                 trade_phase='default/invoicing')
    trade_state = category_tool.trade_state
    business_link_order.setSuccessorValue(trade_state.ordered)
    business_link_deliver.setPredecessorValue(trade_state.ordered)
    business_link_deliver.setSuccessorValue(trade_state.delivered)
    business_link_invoice.setPredecessorValue(trade_state.delivered)
    business_link_invoice.setSuccessorValue(trade_state.invoiced)

    trade_phase = category_tool.trade_phase.default

    self.assertEqual([trade_phase.delivery,
                       trade_phase.invoicing],
                      business_process.getRemainingTradePhaseList(
                       business_process.order))
    self.assertEqual([trade_phase.invoicing],
                      business_process.getRemainingTradePhaseList(
                       business_process.deliver))
    self.assertEqual([],
                      business_process.getRemainingTradePhaseList(
                       business_process.invoice))

  def test_BusinessState_getPreviousTradePhaseDict(self):
    """
    Test for getPreviousTradePhaseDict() and use case for Business
    Links with multiple children (in this test, deliver BL has 2
    children: invoice and tax BL having deliver BL as predecessor).
    """
    category_tool = self.getCategoryTool()
    business_process = self.createBusinessProcess()
    business_link_order = self.createBusinessLink(business_process,
                                 title='order', id='order',
                                 trade_phase='default/order')
    business_link_deliver = self.createBusinessLink(business_process,
                                 title='deliver', id='deliver',
                                 trade_phase='default/delivery')
    business_link_invoice = self.createBusinessLink(business_process,
                                 title='invoice', id='invoice',
                                 trade_phase='default/invoicing')
    business_link_tax = self.createBusinessLink(business_process,
                                 title='tax', id='tax',
                                 trade_phase='default/tax')
    business_link_account = self.createBusinessLink(business_process,
                                 title='accounting', id='account',
                                 trade_phase='default/accounting')

    trade_state = category_tool.trade_state
    business_link_order.setSuccessorValue(trade_state.ordered)
    business_link_deliver.setPredecessorValue(trade_state.ordered)
    business_link_deliver.setSuccessorValue(trade_state.delivered)
    business_link_invoice.setPredecessorValue(trade_state.delivered)
    business_link_invoice.setSuccessorValue(trade_state.invoiced)
    business_link_tax.setPredecessorValue(trade_state.delivered)
    business_link_tax.setSuccessorValue(trade_state.invoiced)
    business_link_account.setPredecessorValue(trade_state.invoiced)
    business_link_account.setSuccessorValue(trade_state.accounted)

    trade_phase = category_tool.trade_phase.default
    def _u(trade_phase):
      return trade_phase.getCategoryRelativeUrl()

    self.assertEqual(
      {_u(trade_phase.order): set(),
       _u(trade_phase.delivery): {_u(trade_phase.order)},
       _u(trade_phase.invoicing): {_u(trade_phase.delivery)},
       _u(trade_phase.tax): {_u(trade_phase.delivery)},
       _u(trade_phase.accounting): {_u(trade_phase.invoicing), _u(trade_phase.tax)}},
      business_process.getPreviousTradePhaseDict())

    self.assertEqual(
      {_u(trade_phase.order): set(),
       _u(trade_phase.invoicing): {_u(trade_phase.order)},
       _u(trade_phase.accounting): {_u(trade_phase.invoicing), _u(trade_phase.order)}},
      business_process.getPreviousTradePhaseDict(
        trade_phase_list=[_u(trade_phase.order),
                          _u(trade_phase.invoicing),
                          _u(trade_phase.accounting)]))

    self.assertEqual(
      {_u(trade_phase.accounting): set()},
      business_process.getPreviousTradePhaseDict(
        trade_phase_list=[_u(trade_phase.accounting)]))

  def test_BusinessProcess_getExpectedTradeModelPathStartAndStopDate(self):
    """
    This test case is described for what start/stop date is expected on
    path by explanation.
    """
    # define business process
    self._createOrderedDeliveredInvoicedBusinessProcess()

    base_date = DateTime('2009/04/01 GMT+9')

    self.constructSimulationTreeAndDeliveries(simulation_depth=1)
    # Set dates manually since we have dummy simulation
    self.simulation_movement.edit(start_date=base_date, stop_date=base_date)
    self.tic()

    def checkExpectedDates(explanation, start_date, stop_date, delay_mode=None):
      self.assertEqual(
        self.business_process.getExpectedTradeModelPathStartAndStopDate(
            explanation, self.delivery_path, delay_mode=delay_mode),
        (start_date, stop_date))

    # Default behavior, no delay
    checkExpectedDates(self.order, base_date, base_date)

    # Update business process in order to introduce delay
    self.delivery_path.edit(min_delay=1.0, max_delay=3.0)
    self.constructSimulationTreeAndDeliveries(simulation_depth=2)
    # Set dates manually since we have dummy simulation
    self.simulation_movement.edit(start_date=base_date, stop_date=base_date)
    checkExpectedDates(self.order, base_date, base_date + 2)
    checkExpectedDates(self.order, base_date, base_date + 1, delay_mode='min')
    checkExpectedDates(self.order, base_date, base_date + 3, delay_mode='max')
    checkExpectedDates(self.delivery_simulation_movement.getParentValue(),
                       base_date, base_date + 2)

    """
    XXX More complex scenarios must be tested, like when several path are
    possible like this :

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

    For now the implementation and documentation is not clear enough.
    """

  def test_isBuildable(self):
    """Test isBuildable for ordered, delivered and invoiced sequence

    Here Business Process sequence corresponds simulation tree.

    delivery_path is related to root applied rule, and invoice_path is related
    to rule below, and invoice_path is after delivery_path
    """
    self._createOrderedDeliveredInvoicedBusinessProcess()
    self.constructSimulationTreeAndDeliveries(dummy_split=True)

    self.order.setSimulationState(self.completed_state)
    self.tic()

    def checkIsBusinessLinkBuildable(explanation, business_link, value):
      self.assertEqual(self.business_process.isBusinessLinkBuildable(
       explanation, business_link), value)

    # in the beginning only order related movements shall be buildable
    checkIsBusinessLinkBuildable(self.order, self.delivery_link, True)
    self.assertEqual(self.delivery_simulation_movement.isBuildable(), True)
    self.assertEqual(self.split_delivery_simulation_movement.isBuildable(), True)

    checkIsBusinessLinkBuildable(self.order, self.invoice_link, False)
    self.assertEqual(self.invoicing_simulation_movement.isBuildable(), False)
    self.assertEqual(self.split_invoicing_simulation_movement.isBuildable(),
        False)

    # add delivery
    delivery = self._createDelivery(causality_value = self.order)
    delivery_line = self._createMovement(delivery)

    # relate not split movement with delivery (deliver it)
    self.delivery_simulation_movement.edit(delivery_value = delivery_line)

    self.tic()

    # delivery_link (for order) is still buildable, as split movement is not
    # delivered yet
    #
    # invoice_link is not yet buildable, delivery is in inproper simulation
    # state
    #
    # delivery_link (for delivery) is not buildable - delivery is already
    # built for those movements
    checkIsBusinessLinkBuildable(self.order, self.delivery_link, True)
    self.assertEqual(self.split_delivery_simulation_movement.isBuildable(), True)

    checkIsBusinessLinkBuildable(delivery, self.delivery_link, False)
    checkIsBusinessLinkBuildable(delivery, self.invoice_link, False)
    self.assertEqual(self.delivery_simulation_movement.isBuildable(), False)
    self.assertEqual(self.invoicing_simulation_movement.isBuildable(), False)
    checkIsBusinessLinkBuildable(self.order, self.invoice_link, False)
    self.assertEqual(self.split_invoicing_simulation_movement.isBuildable(), False)

    # put delivery in simulation state configured on path (and this state is
    # available directly on movements)

    delivery.setSimulationState(self.completed_state)

    self.assertEqual(self.completed_state, delivery.getSimulationState())

    self.tic()

    # delivery_link (for order) is still buildable, as split movement is not
    # delivered yet
    #
    # invoice_link is not buildable in case of order because delivery_link
    # is not completed yet.
    #
    # invoice link is buildable for delivery because part of tree is buildable
    #
    # split movement for invoicing is not buildable - no proper delivery
    # related for previous path
    checkIsBusinessLinkBuildable(self.order, self.delivery_link, True)
    self.assertEqual(self.invoicing_simulation_movement.isBuildable(), True)
    checkIsBusinessLinkBuildable(delivery, self.invoice_link, True)

    checkIsBusinessLinkBuildable(self.order, self.invoice_link, False)
    checkIsBusinessLinkBuildable(delivery, self.invoice_link, True)
    checkIsBusinessLinkBuildable(delivery, self.delivery_link, False)
    self.assertEqual(self.delivery_simulation_movement.isBuildable(), False)
    self.assertEqual(self.split_invoicing_simulation_movement.isBuildable(),
        False)

  def test_isCompleted(self):
    """Test isCompleted for ordered, delivered and invoiced sequence"""
    self._createOrderedDeliveredInvoicedBusinessProcess()
    self.constructSimulationTreeAndDeliveries(dummy_split=True)

    self.assertEqual(self.delivery_link.isCompleted(self.order), False)
    self.assertEqual(self.delivery_link.isPartiallyCompleted(self.order), False)

    self.assertEqual(self.invoice_link.isCompleted(self.order), False)
    self.assertEqual(self.invoice_link.isPartiallyCompleted(self.order), False)

    # add delivery
    delivery = self._createDelivery(causality_value = self.order)
    delivery_line = self._createMovement(delivery)

    # relate not split movement with delivery (deliver it)
    self.delivery_simulation_movement.edit(delivery_value = delivery_line)

    self.tic()

    # nothing changes
    self.assertEqual(self.delivery_link.isCompleted(self.order), False)
    self.assertEqual(self.delivery_link.isPartiallyCompleted(self.order), False)

    self.assertEqual(self.invoice_link.isCompleted(self.order), False)
    self.assertEqual(self.invoice_link.isPartiallyCompleted(self.order), False)

    # from delivery point of view everything is same
    self.assertEqual(self.delivery_link.isCompleted(delivery), False)
    self.assertEqual(self.delivery_link.isPartiallyCompleted(delivery), False)

    self.assertEqual(self.invoice_link.isCompleted(delivery), False)
    self.assertEqual(self.invoice_link.isPartiallyCompleted(delivery), False)

    # put delivery in simulation state configured on path (and this state is
    # available directly on movements)

    delivery.setSimulationState(self.completed_state)

    self.assertEqual(self.completed_state, delivery.getSimulationState())

    self.tic()

    self.assertEqual(self.delivery_link.isCompleted(self.order), False)
    self.assertEqual(self.delivery_link.isPartiallyCompleted(self.order), True)

    self.assertEqual(self.invoice_link.isCompleted(self.order), False)
    self.assertEqual(self.invoice_link.isPartiallyCompleted(self.order), False)

    self.assertEqual(self.delivery_link.isCompleted(delivery), True)
    self.assertEqual(self.delivery_link.isPartiallyCompleted(delivery), True)

    self.assertEqual(self.invoice_link.isCompleted(delivery), False)
    self.assertEqual(self.invoice_link.isPartiallyCompleted(delivery), False)

    # and finally deliver everything simulation movement coming from order
    another_delivery = self._createDelivery()
    another_delivery_line = self._createMovement(another_delivery)
    self.split_delivery_simulation_movement.edit(
      delivery_value=another_delivery_line)
    another_delivery.setSimulationState(self.completed_state)
    self.tic()

    self.assertEqual(self.delivery_link.isCompleted(self.order), True)
    self.assertEqual(self.delivery_link.isPartiallyCompleted(self.order), True)

  def test_isFrozen_OrderedDeliveredInvoiced(self):
    """Test isFrozen for ordered, delivered and invoiced sequence"""
    self._createOrderedDeliveredInvoicedBusinessProcess()
    self.constructSimulationTreeAndDeliveries(dummy_split=True)

    self.assertEqual(self.order_link.isFrozen(self.order), False)
    self.assertEqual(self.delivery_link.isFrozen(self.order), False)
    self.assertEqual(self.invoice_link.isFrozen(self.order), False)
    self.assertEqual(self.simulation_movement.isFrozen(), False)
    self.assertEqual(self.split_simulation_movement.isFrozen(), False)

    self.order.setSimulationState(self.completed_state)
    self.tic()
    self.assertEqual(self.order_link.isFrozen(self.order), True)
    self.assertEqual(self.delivery_link.isFrozen(self.order), False)

    self.assertEqual(self.simulation_movement.isFrozen(), True)
    self.assertEqual(self.invoicing_simulation_movement.isFrozen(), False)
    self.assertEqual(self.split_simulation_movement.isFrozen(), True)
    self.assertEqual(self.split_invoicing_simulation_movement.isFrozen(), False)

    # add delivery
    delivery = self._createDelivery()
    delivery_line = self._createMovement(delivery)

    # relate not split movement with delivery (deliver it)
    self.delivery_simulation_movement.edit(delivery_value = delivery_line)

    self.tic()

    # nothing changes
    self.assertEqual(self.delivery_link.isFrozen(self.order), False)
    self.assertEqual(self.invoice_link.isFrozen(self.order), False)

    # from delivery point of view everything is same
    self.assertEqual(self.delivery_link.isFrozen(delivery), False)
    self.assertEqual(self.invoice_link.isFrozen(delivery), False)

    self.assertEqual(self.simulation_movement.isFrozen(), True)
    self.assertEqual(self.invoicing_simulation_movement.isFrozen(), False)
    self.assertEqual(self.split_simulation_movement.isFrozen(), True)
    self.assertEqual(self.split_invoicing_simulation_movement.isFrozen(), False)

    # put delivery in simulation state configured on path (and this state is
    # available directly on movements)

    delivery.setSimulationState(self.frozen_state)

    self.assertEqual(self.frozen_state, delivery.getSimulationState())

    self.tic()

    self.assertEqual(self.delivery_link.isFrozen(self.order), False)
    self.assertEqual(self.invoice_link.isFrozen(self.order), False)
    self.assertEqual(self.delivery_link.isFrozen(delivery), True)
    self.assertEqual(self.invoice_link.isFrozen(delivery), False)

    self.assertEqual(self.delivery_simulation_movement.isFrozen(), True)
    self.assertEqual(self.invoicing_simulation_movement.isFrozen(), False)
    self.assertEqual(self.split_simulation_movement.isFrozen(), True)
    self.assertEqual(self.split_invoicing_simulation_movement.isFrozen(), False)

  @todo_erp5
  def test_payBeforeDelivery(self):
    # TODO: Implement use cases where business states don't follow the order
    #       of applied rules.
    #       This was tested in draft implementation of BPM
    #       (see testBPMEvaluation in older revisions).
    raise NotImplementedError

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestBPMImplementation))
  return suite
