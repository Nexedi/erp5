# -*- coding: utf-8 -*-
##############################################################################
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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
from AccessControl.SecurityManagement import newSecurityManager
from DateTime import DateTime

from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.tests.utils import reindex

from Products.ERP5.tests.testBPMCore import TestBPMMixin

class TestMRPMixin(TestBPMMixin):
  transformation_portal_type = 'Transformation'
  transformed_resource_portal_type = 'Transformation Transformed Resource'
  product_portal_type = 'Product'
  organisation_portal_type = 'Organisation'
  order_portal_type = 'Production Order'
  order_line_portal_type = 'Production Order Line'

  def setUpOnce(self):
    self.portal = self.getPortalObject()

  def invalidateRules(self):
    """
    do reversely of validateRules
    """
    rule_tool = self.getRuleTool()
    for rule in rule_tool.contentValues(
      portal_type=rule_tool.getPortalRuleTypeList()):
      rule.invalidate()

  def _createDocument(self, portal_type, **kw):
    module = self.portal.getDefaultModule(
        portal_type=portal_type)
    return self._createObject(module, portal_type, **kw)

  def _createObject(self, parent, portal_type, id=None, **kw):
    o = None
    if id is not None:
      o = parent.get(str(id), None)
    if o is None:
      o = parent.newContent(portal_type=portal_type)
    o.edit(**kw)
    return o

  def createTransformation(self, **kw):
    return self._createDocument(self.transformation_portal_type, **kw)

  def createProduct(self, **kw):
    return self._createDocument(self.product_portal_type, **kw)

  def createOrganisation(self, **kw):
    return self._createDocument(self.organisation_portal_type, **kw)

  def createOrder(self, **kw):
    return self._createDocument(self.order_portal_type, **kw)

  def createOrderLine(self, order, **kw):
    return self._createObject(order, self.order_line_portal_type, **kw)

  def createTransformedResource(self, transformation, **kw):
    return self._createObject(transformation, self.transformed_resource_portal_type, **kw)

  @reindex
  def createCategories(self):
    category_tool = getToolByName(self.portal, 'portal_categories')
    self.createCategoriesInCategory(category_tool.base_amount, ['weight'])
    self.createCategoriesInCategory(category_tool.base_amount.weight, ['kg'])
    self.createCategoriesInCategory(category_tool.trade_phase, ['mrp',])
    self.createCategoriesInCategory(category_tool.trade_phase.mrp,
        ['p' + str(i) for i in range(5)]) # phase0 ~ 4

  @reindex
  def createDefaultOrder(self, transformation=None, business_process=None):
    if transformation is None:
      transformation = self.createDefaultTransformation()
    if business_process is None:
      business_process = self.createSimpleBusinessProcess()

    base_date = DateTime()

    order = self.createOrder(specialise_value=business_process,
                             start_date=base_date,
                             stop_date=base_date+3)
    order_line = self.createOrderLine(order,
                                      quantity=10,
                                      resource=transformation.getResource(),
                                      specialise_value=transformation)
    # XXX in some case, specialise_value is not related to order_line by edit,
    #     but by setSpecialise() is ok, Why?
    order_line.setSpecialiseValue(transformation)
    return order
    
  @reindex
  def createDefaultTransformation(self):
    resource1 = self.createProduct(id='1', quantity_unit_list=['weight/kg'])
    resource2 = self.createProduct(id='2', quantity_unit_list=['weight/kg'])
    resource3 = self.createProduct(id='3', quantity_unit_list=['weight/kg'])
    resource4 = self.createProduct(id='4', quantity_unit_list=['weight/kg'])
    resource5 = self.createProduct(id='5', quantity_unit_list=['weight/kg'])

    transformation = self.createTransformation(resource_value=resource5)
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource1,
                                   quantity=3,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p2')
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource2,
                                   quantity=1,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p2')
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource3,
                                   quantity=4,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p3')
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource4,
                                   quantity=1,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p3')
    return transformation

  @reindex
  def createSimpleBusinessProcess(self):
    """    mrp/p2                    mrp/3
    ready -------- partial_produced ------- done
    """
    business_process = self.createBusinessProcess()
    business_path_p2 = self.createBusinessPath(business_process)
    business_path_p3 = self.createBusinessPath(business_process)
    business_state_ready = self.createBusinessState(business_process)
    business_state_partial = self.createBusinessState(business_process)
    business_state_done = self.createBusinessState(business_process)

    # organisations
    source_section = self.createOrganisation(title='source_section')
    source = self.createOrganisation(title='source')
    destination_section = self.createOrganisation(title='destination_section')
    destination = self.createOrganisation(title='destination')
    
    business_process.edit(referential_date='stop_date')
    business_path_p2.edit(id='p2',
                          predecessor_value=business_state_ready,
                          successor_value=business_state_partial,
                          quantity=1,
                          trade_phase=['mrp/p2'],
                          source_section_value=source_section,
                          source_value=source,
                          destination_section_value=destination_section,
                          destination_value=destination,
                          )
    business_path_p3.edit(id='p3',
                          predecessor_value=business_state_partial,
                          successor_value=business_state_done,
                          quantity=1,
                          deliverable=1, # root explanation
                          trade_phase=['mrp/p3'],
                          source_section_value=source_section,
                          source_value=source,
                          destination_section_value=destination_section,
                          destination_value=destination,
                          )
    return business_process

  @reindex
  def createConcurrentBusinessProcess(self):
    """    mrp/p2
    ready ======== partial_produced
           mrp/p3
    """
    business_process = self.createBusinessProcess()
    business_path_p2 = self.createBusinessPath(business_process)
    business_path_p3 = self.createBusinessPath(business_process)
    business_state_ready = self.createBusinessState(business_process)
    business_state_partial = self.createBusinessState(business_process)

    # organisations
    source_section = self.createOrganisation(title='source_section')
    source = self.createOrganisation(title='source')
    destination_section = self.createOrganisation(title='destination_section')
    destination = self.createOrganisation(title='destination')

    business_process.edit(referential_date='stop_date')
    business_path_p2.edit(id='p2',
                          predecessor_value=business_state_ready,
                          successor_value=business_state_partial,
                          quantity=1,
                          trade_phase=['mrp/p2'],
                          source_section_value=source_section,
                          source_value=source,
                          destination_section_value=destination_section,
                          destination_value=destination,
                          )
    business_path_p3.edit(id='p3',
                          predecessor_value=business_state_ready,
                          successor_value=business_state_partial,
                          quantity=1,
                          deliverable=1, # root explanation
                          trade_phase=['mrp/p3'],
                          source_section_value=source_section,
                          source_value=source,
                          destination_section_value=destination_section,
                          destination_value=destination,
                          )
    return business_process

  @reindex
  def beforeTearDown(self):
    super(TestMRPMixin, self).beforeTearDown()
    transaction.abort()
    for module in (
      self.portal.organisation_module,
      self.portal.production_order_module, 
      self.portal.transformation_module,
      self.portal.business_process_module,
      # don't remove document because reuse it for testing of id
      # self.portal.product_module,
      self.portal.portal_simulation,):    
      module.manage_delObjects(list(module.objectIds()))
    transaction.commit()

class TestMRPImplementation(TestMRPMixin, ERP5TypeTestCase):
  """the test for implementation"""
  def test_TransformationRule_getHeadProductionPathList(self):
    rule = self.portal.portal_rules.default_transformation_model_rule

    transformation = self.createDefaultTransformation()

    business_process = self.createSimpleBusinessProcess()
    self.assertEquals([business_process.p2],
                      rule.getHeadProductionPathList(transformation, business_process))

    business_process = self.createConcurrentBusinessProcess()
    self.assertEquals(set([business_process.p2, business_process.p3]),
                      set(rule.getHeadProductionPathList(transformation, business_process)))

  def test_TransformationRule_expand(self):
    # mock order
    order = self.createDefaultOrder()
    order_line = order.objectValues()[0]

    business_process = order.getSpecialiseValue()

    # paths
    path_p2 = '%s/p2' % business_process.getRelativeUrl()
    path_p3 = '%s/p3' % business_process.getRelativeUrl()

    # organisations
    path = business_process.objectValues(
      portal_type=self.portal.getPortalBusinessPathTypeList())[0]
    source_section = path.getSourceSection()
    source = path.getSource()
    destination_section = path.getDestinationSection()
    destination = path.getDestination()
    consumed_organisations = (source_section, source, destination_section, None)
    produced_organisations = (source_section, None, destination_section, destination)

    # don't need another rules, just need TransformationRule for test
    self.invalidateRules()

    self.stepTic()

    # alter simulations of the order
    # root
    applied_rule = self.portal.portal_simulation.newContent(portal_type='Applied Rule')
    movement = applied_rule.newContent(portal_type='Simulation Movement')
    applied_rule.edit(causality_value=order)
    movement.edit(order_value=order_line,
                  quantity=order_line.getQuantity(),
                  resource=order_line.getResource())
    # test mock
    applied_rule = movement.newContent(potal_type='Applied Rule')

    rule = self.portal.portal_rules.default_transformation_model_rule
    rule.expand(applied_rule)

    # assertion
    expected_value_set = set([
      ((path_p2,), 'product_module/5', produced_organisations, 'mrp/p3', -10),
      ((path_p2,), 'product_module/1', consumed_organisations, 'mrp/p2', 30),
      ((path_p2,), 'product_module/2', consumed_organisations, 'mrp/p2', 10),
      ((path_p3,), 'product_module/5', consumed_organisations, 'mrp/p3', 10),
      ((path_p3,), 'product_module/3', consumed_organisations, 'mrp/p3', 40),
      ((path_p3,), 'product_module/4', consumed_organisations, 'mrp/p3', 10),
      ((path_p3,), 'product_module/5', produced_organisations, None, -10)])
    movement_list = applied_rule.objectValues()
    self.assertEquals(len(expected_value_set), len(movement_list))
    movement_value_set = set([])
    for movement in movement_list:
      movement_value_set |= set([(tuple(movement.getCausalityList()),
                                  movement.getResource(),
                                  (movement.getSourceSection(),
                                   movement.getSource(),
                                   movement.getDestinationSection(),
                                   movement.getDestination(),), # organisations
                                  movement.getTradePhase(),
                                  movement.getQuantity())])
    self.assertEquals(expected_value_set, movement_value_set)

  def test_TransformationRule_expand_concurrent(self):
    business_process = self.createConcurrentBusinessProcess()

    # mock order
    order = self.createDefaultOrder(business_process=business_process)
    order_line = order.objectValues()[0]

    # phases
    phase_p2 = '%s/p2' % business_process.getRelativeUrl()
    phase_p3 = '%s/p3' % business_process.getRelativeUrl()

    # organisations
    path = business_process.objectValues(
      portal_type=self.portal.getPortalBusinessPathTypeList())[0]
    source_section = path.getSourceSection()
    source = path.getSource()
    destination_section = path.getDestinationSection()
    destination = path.getDestination()
    organisations = (source_section, source, destination_section, destination)
    consumed_organisations = (source_section, source, destination_section, None)
    produced_organisations = (source_section, None, destination_section, destination)

    # don't need another rules, just need TransformationRule for test
    self.invalidateRules()

    self.stepTic()

    # alter simulations of the order
    # root
    applied_rule = self.portal.portal_simulation.newContent(portal_type='Applied Rule')
    movement = applied_rule.newContent(portal_type='Simulation Movement')
    applied_rule.edit(causality_value=order)
    movement.edit(order_value=order_line,
                  quantity=order_line.getQuantity(),
                  resource=order_line.getResource())
    # test mock
    applied_rule = movement.newContent(potal_type='Applied Rule')

    rule = self.portal.portal_rules.default_transformation_model_rule
    rule.expand(applied_rule)

    # assertion
    expected_value_set = set([
      ((phase_p2,), 'product_module/1', consumed_organisations, 'mrp/p2', 30),
      ((phase_p2,), 'product_module/2', consumed_organisations, 'mrp/p2', 10),
      ((phase_p3,), 'product_module/3', consumed_organisations, 'mrp/p3', 40),
      ((phase_p3,), 'product_module/4', consumed_organisations, 'mrp/p3', 10),
      ((phase_p2, phase_p3), 'product_module/5', produced_organisations, None, -10)])
    movement_list = applied_rule.objectValues()
    self.assertEquals(len(expected_value_set), len(movement_list))
    movement_value_set = set([])
    for movement in movement_list:
      movement_value_set |= set([(tuple(movement.getCausalityList()),
                                  movement.getResource(),
                                  (movement.getSourceSection(),
                                   movement.getSource(),
                                   movement.getDestinationSection(),
                                   movement.getDestination(),), # organisations
                                  movement.getTradePhase(),
                                  movement.getQuantity())])
    self.assertEquals(expected_value_set, movement_value_set)

  def test_TransformationRule_expand_reexpand(self):
    """
    test case of difference when any movement are frozen
    by using above result
    """
    self.test_TransformationRule_expand_concurrent()

    self.stepTic()

    applied_rule = self.portal.portal_simulation.objectValues()[0]

    business_process = applied_rule.getCausalityValue().getSpecialiseValue()

    # phases
    phase_p2 = '%s/p2' % business_process.getRelativeUrl()
    phase_p3 = '%s/p3' % business_process.getRelativeUrl()

    # organisations
    path = business_process.objectValues(
      portal_type=self.portal.getPortalBusinessPathTypeList())[0]
    source_section = path.getSourceSection()
    source = path.getSource()
    destination_section = path.getDestinationSection()
    destination = path.getDestination()
    consumed_organisations = (source_section, source, destination_section, None)
    produced_organisations = (source_section, None, destination_section, destination)

    movement = applied_rule.objectValues()[0]
    applied_rule = movement.objectValues()[0]

    # these movements are made by transformation
    for movement in applied_rule.objectValues():
      movement.edit(quantity=1)
      # set the state value of isFrozen to 1,
      movement._baseSetFrozen(1)

    # re-expand
    rule = self.portal.portal_rules.default_transformation_model_rule
    rule.expand(applied_rule)

    # assertion
    expected_value_set = set([
      ((phase_p2,), 'product_module/1', consumed_organisations, 'mrp/p2', 1), # Frozen
      ((phase_p2,), 'product_module/1', consumed_organisations, 'mrp/p2', 29),
      ((phase_p2,), 'product_module/2', consumed_organisations, 'mrp/p2', 1), # Frozen
      ((phase_p2,), 'product_module/2', consumed_organisations, 'mrp/p2', 9),
      ((phase_p3,), 'product_module/3', consumed_organisations, 'mrp/p3', 1), # Frozen
      ((phase_p3,), 'product_module/3', consumed_organisations, 'mrp/p3', 39),
      ((phase_p3,), 'product_module/4', consumed_organisations, 'mrp/p3', 1), # Frozen
      ((phase_p3,), 'product_module/4', consumed_organisations, 'mrp/p3', 9),
      ((phase_p2, phase_p3), 'product_module/5', produced_organisations, None, 1), # Frozen
      ((phase_p2, phase_p3), 'product_module/5', produced_organisations, None, -11)])
    movement_list = applied_rule.objectValues()
    self.assertEquals(len(expected_value_set), len(movement_list))
    movement_value_set = set([])
    for movement in movement_list:
      movement_value_set |= set([(tuple(movement.getCausalityList()),
                                  movement.getResource(),
                                  (movement.getSourceSection(),
                                   movement.getSource(),
                                   movement.getDestinationSection(),
                                   movement.getDestination(),), # organisations
                                  movement.getTradePhase(),
                                  movement.getQuantity())])
    self.assertEquals(expected_value_set, movement_value_set)

  def test_TransformationSourcingRule_expand(self):
    # mock order
    order = self.createDefaultOrder()
    order_line = order.objectValues()[0]

    # don't need another rules, just need TransformationSourcingRule for test
    self.invalidateRules()

    self.stepTic()

    business_process = order.getSpecialiseValue()

    # get last path of a business process
    # in simple business path, the last is between "partial_produced" and "done"
    causality_path = None
    for state in business_process.objectValues(
      portal_type=self.portal.getPortalBusinessStateTypeList()):
      if len(state.getRemainingTradePhaseList(self.portal)) == 0:
        causality_path = state.getSuccessorRelatedValue()

    # phases
    phase_p2 = '%s/p2' % business_process.getRelativeUrl()

    # organisations
    source_section = causality_path.getSourceSection()
    source = causality_path.getSource()
    destination_section = causality_path.getDestinationSection()
    destination = causality_path.getDestination()
    organisations = (source_section, source, destination_section, destination)

    # sourcing resource
    sourcing_resource = order_line.getResource()

    # alter simulations of the order
    # root
    applied_rule = self.portal.portal_simulation.newContent(portal_type='Applied Rule')
    movement = applied_rule.newContent(portal_type='Simulation Movement')
    applied_rule.edit(causality_value=order)
    movement.edit(order_value=order_line,
                  causality_value=causality_path,
                  quantity=order_line.getQuantity(),
                  resource=sourcing_resource,
                  )

    self.stepTic()

    # test mock
    applied_rule = movement.newContent(potal_type='Applied Rule')

    rule = self.portal.portal_rules.default_transformation_sourcing_model_rule
    rule.expand(applied_rule)

    # assertion
    expected_value_set = set([
      ((phase_p2,), sourcing_resource, organisations, 10)])
    movement_list = applied_rule.objectValues()
    self.assertEquals(len(expected_value_set), len(movement_list))
    movement_value_set = set([])
    for movement in movement_list:
      movement_value_set |= set([(tuple(movement.getCausalityList()),
                                  movement.getResource(),
                                  (movement.getSourceSection(),
                                   movement.getSource(),
                                   movement.getDestinationSection(),
                                   movement.getDestination(),), # organisations
                                  movement.getQuantity())])
    self.assertEquals(expected_value_set, movement_value_set)


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestMRPImplementation))
  return suite
