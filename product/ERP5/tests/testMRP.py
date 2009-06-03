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

from Products.ERP5.Document.TransformationRule import TransformationRule

from Products.ERP5.tests.testBPMCore import TestBPMMixin

class TestMRPMixin(TestBPMMixin):
  transformation_portal_type = 'Transformation'
  transformed_resource_portal_type = 'Transformation Transformed Resource'
  product_portal_type = 'Product'

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
    
  def createTransformation(self):
    module = self.portal.getDefaultModule(
        portal_type=self.transformation_portal_type)
    return module.newContent(portal_type=self.transformation_portal_type)

  def createTransformedResource(self, transformation=None):
    if transformation is None:
      transformation = self.createTransformation()
    return transformation.newContent(
      portal_type=self.transformed_resource_portal_type)

  @reindex
  def createCategories(self):
    category_tool = getToolByName(self.portal, 'portal_categories')
    self.createCategoriesInCategory(category_tool.base_amount, ['weight'])
    self.createCategoriesInCategory(category_tool.base_amount.weight, ['kg'])
    self.createCategoriesInCategory(category_tool.trade_phase, ['mrp',])
    self.createCategoriesInCategory(category_tool.trade_phase.mrp,
        ['p' + str(i) for i in range(5)]) # phase0 ~ 4

  def createProduct(self):
    module = self.portal.getDefaultModule(
      portal_type=self.product_portal_type)
    return module.newContent(portal_type=self.product_portal_type)

  @reindex
  def createDefaultTransformation(self):
    resource1 = self.createProduct()
    resource2 = self.createProduct()
    resource3 = self.createProduct()
    resource4 = self.createProduct()
    resource5 = self.createProduct()
    transformation = self.createTransformation()
    amount1 = self.createTransformedResource(transformation=transformation)
    amount2 = self.createTransformedResource(transformation=transformation)
    amount3 = self.createTransformedResource(transformation=transformation)
    amount4 = self.createTransformedResource(transformation=transformation)

    resource1.edit(title='product', quantity_unit_list=['weight/kg'])
    resource2.edit(title='triangle', quantity_unit_list=['weight/kg'])
    resource3.edit(title='box', quantity_unit_list=['weight/kg'])
    resource4.edit(title='circle', quantity_unit_list=['weight/kg'])
    resource5.edit(title='banana', quantity_unit_list=['weight/kg'])

    transformation.edit(resource_value=resource1)
    amount1.edit(resource_value=resource2, quantity=3,
                 quantity_unit_list=['weight/kg'], trade_phase='mrp/p2')
    amount2.edit(resource_value=resource3, quantity=1,
                 quantity_unit_list=['weight/kg'], trade_phase='mrp/p2')
    amount3.edit(resource_value=resource4, quantity=4,
                 quantity_unit_list=['weight/kg'], trade_phase='mrp/p3')
    amount4.edit(resource_value=resource5, quantity=1,
                 quantity_unit_list=['weight/kg'], trade_phase='mrp/p3')
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

    business_process.edit(referential_date='stop_date')
    business_path_p2.edit(id='p2',
                          predecessor_value=business_state_ready,
                          successor_value=business_state_partial,
                          quantity=1,
                          trade_phase=['mrp/p2'])
    business_path_p3.edit(id='p3',
                          predecessor_value=business_state_partial,
                          successor_value=business_state_done,
                          quantity=1,
                          deliverable=1, # root explanation
                          trade_phase=['mrp/p3'])
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

    business_process.edit(referential_date='stop_date')
    business_path_p2.edit(id='p2',
                          predecessor_value=business_state_ready,
                          successor_value=business_state_partial,
                          quantity=1,
                          trade_phase=['mrp/p2'])
    business_path_p3.edit(id='p3',
                          predecessor_value=business_state_ready,
                          successor_value=business_state_partial,
                          quantity=1,
                          deliverable=1, # root explanation
                          trade_phase=['mrp/p3'])
    return business_process

class TestMRPImplementation(TestMRPMixin, ERP5TypeTestCase):
  """the test for implementation"""
  def test_TransformationRule_getHeadProductionPathList(self):
    rule = self.portal.portal_rules.default_transformation_rule

    transformation = self.createDefaultTransformation()

    business_process = self.createSimpleBusinessProcess()
    self.assertEquals([business_process.p2],
                      rule.getHeadProductionPathList(transformation, business_process))

    business_process = self.createConcurrentBusinessProcess()
    self.assertEquals(set([business_process.p2, business_process.p3]),
                      set(rule.getHeadProductionPathList(transformation, business_process)))

  def test_TransformationRule_expand(self):
    transformation = self.createDefaultTransformation()

    """
      Simple case
    """
    business_process = self.createSimpleBusinessProcess()

    # mock order
    order = self.portal.production_order_module.newContent(portal_type="Production Order")
    order_line = order.newContent(portal_type="Production Order Line")

    base_date = DateTime()
    order.edit(specialise_value=business_process,
               start_date=base_date,
               stop_date=base_date+3,
               source_section_value=order,
               source_value=order)
    order_line.edit(quantity=10)
    order_line.setSpecialiseValue(transformation) # XXX Why can not define by edit?

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
                  resource=transformation.getResource())
    # test mock
    applied_rule = movement.newContent(potal_type='Applied Rule')

    rule = self.portal.portal_rules.default_transformation_rule
    rule.expand(applied_rule)

    # assertion
    expected_value_set = set([
      (('business_process_module/1/p2',), 'product_module/1', 'mrp/p3', -10),
      (('business_process_module/1/p2',), 'product_module/2', 'mrp/p2', 30),
      (('business_process_module/1/p2',), 'product_module/3', 'mrp/p2', 10),
      (('business_process_module/1/p3',), 'product_module/1', 'mrp/p3', 10),
      (('business_process_module/1/p3',), 'product_module/4', 'mrp/p3', 40),
      (('business_process_module/1/p3',), 'product_module/5', 'mrp/p3', 10),
      (('business_process_module/1/p3',), 'product_module/1', None, -10)])
    movement_list = applied_rule.objectValues()
    self.assertEquals(len(expected_value_set), len(movement_list))
    movement_value_set = set([])
    for movement in movement_list:
      movement_value_set |= set([(tuple(movement.getCausalityList()),
                                  movement.getResource(),
                                  movement.getTradePhase(),
                                  movement.getQuantity())])
    self.assertEquals(expected_value_set, movement_value_set)

    """
      Concurrent case
    """
    business_process = self.createConcurrentBusinessProcess()
    order.edit(specialise_value=business_process)

    self.stepTic()

    # alter simulations of the order
    # root
    applied_rule = self.portal.portal_simulation.newContent(portal_type='Applied Rule')
    movement = applied_rule.newContent(portal_type='Simulation Movement')
    applied_rule.edit(causality_value=order)
    movement.edit(order_value=order_line,
                  quantity=order_line.getQuantity(),
                  resource=transformation.getResource())
    # test mock
    applied_rule = movement.newContent(potal_type='Applied Rule')

    rule = self.portal.portal_rules.default_transformation_rule
    rule.expand(applied_rule)

    # assertion
    expected_value_set = set([
      (('business_process_module/2/p2',), 'product_module/2', 'mrp/p2', 30),
      (('business_process_module/2/p2',), 'product_module/3', 'mrp/p2', 10),
      (('business_process_module/2/p3',), 'product_module/4', 'mrp/p3', 40),
      (('business_process_module/2/p3',), 'product_module/5', 'mrp/p3', 10),
      (('business_process_module/2/p2', 'business_process_module/2/p3'), 'product_module/1', None, -10)])
    movement_list = applied_rule.objectValues()
    self.assertEquals(len(expected_value_set), len(movement_list))
    movement_value_set = set([])
    for movement in movement_list:
      movement_value_set |= set([(tuple(movement.getCausalityList()),
                                  movement.getResource(),
                                  movement.getTradePhase(),
                                  movement.getQuantity())])
    self.assertEquals(expected_value_set, movement_value_set)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestMRPImplementation))
  return suite
