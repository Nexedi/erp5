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
from DateTime import DateTime
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from Products.ERP5.tests.testBPMCore import TestBPMMixin

class TestMRPMixin(TestBPMMixin):

  def afterSetUp(self):
    super(TestMRPMixin, self).afterSetUp()
    self._createRule("Transformation Simulation Rule")
    rule = self._createRule("Transformation Sourcing Simulation Rule")
    rule._setSameTotalQuantity(False)

  def getBusinessTemplateList(self):
    return TestBPMMixin.getBusinessTemplateList(self) + ('erp5_mrp', )

  def _createRule(self, portal_type):
    x = portal_type.replace(' Simulation ', ' ').replace(' ', '_').lower()
    reference = "default_" + x
    id = "testMRP_" + x
    rule_tool = self.portal.portal_rules
    try:
      rule = self.getRule(reference=reference)
      self.assertEqual(rule.getId(), id)
    except IndexError:
      rule = rule_tool.newContent(id, portal_type,
        reference=reference,
        test_method_id="SimulationMovement_test" + portal_type.replace(' ', ''))
      def newTester(p, t, **kw):
        kw.setdefault("tested_property", (p,))
        return rule.newContent(p  + "_tester", t + " Divergence Tester",
                               title=p + " divergence tester", **kw)
      for x in ("aggregate",
                "base_application",
                "base_contribution",
                "destination_section",
                "destination",
                "price_currency",
                "resource",
                "source_section",
                "source",
                "use"):
        newTester(x, "Category Membership")
      for x in ("start_date", "stop_date"):
        newTester(x, "DateTime")
      newTester("price", "Float")
      newTester("quantity", "Net Converted Quantity",
                tested_property=("quantity", "quantity_unit"))
      newTester("specialise", "Specialise")
      newTester("variation", "Variation",
                tested_property=("variation_category_list",
                                 "variation_property_dict"))
      newTester("reference", "String",  matching_provider=1,
                                        divergence_provider=0)
    if rule.getValidationState() != 'validated':
      rule.validate()
    return rule

  def _createDocument(self, portal_type, **kw):
    return self.portal.getDefaultModule(portal_type=portal_type).newContent(
      portal_type=portal_type, **kw)

  def createTransformation(self, **kw):
    return self._createDocument('Transformation', **kw)

  def createProduct(self, **kw):
    return self._createDocument('Product', **kw)

  def createNode(self, **kw):
    return self._createDocument('Organisation', **kw)

  def createOrder(self, **kw):
    return self._createDocument('Production Order', **kw)

  def createOrderLine(self, order, **kw):
    return order.newContent(portal_type=order.getPortalType() + ' Line', **kw)

  def createTransformedResource(self, transformation, **kw):
    return transformation.newContent(
      portal_type='Transformation Transformed Resource', **kw)

  def createCategories(self):
    category_tool = self.portal.portal_categories
    self.createCategoriesInCategory(category_tool.quantity_unit, ['weight'])
    self.createCategoriesInCategory(category_tool.quantity_unit.weight, ['kg'])
    self.createCategoriesInCategory(category_tool.trade_phase, ['mrp',])
    self.createCategoriesInCategory(category_tool.trade_phase.mrp,
        ('p' + str(i) for i in xrange(2)))
    self.createCategoriesInCategory(category_tool.trade_phase.mrp,
        ('s' + str(i) for i in xrange(1)))
    self.createCategoriesInCategory(category_tool.trade_state,
        ('s' + str(i) for i in xrange(5)))

  def createDefaultOrder(self, business_process, transformation=None):
    if transformation is None:
      transformation = self.createDefaultTransformation()
    base_date = DateTime()
    order = self.createOrder(specialise_value=business_process,
                             start_date=base_date,
                             stop_date=base_date+3)
    order_line = self.createOrderLine(order,
                                      quantity=10,
                                      resource=transformation.getResource(),
                                      specialise_value=transformation)
    return order

  def createDefaultTransformation(self):
    resource = lambda: self.createProduct(quantity_unit_list=['weight/kg'])
    transformation = self.createTransformation(resource_value=resource())
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource(),
                                   quantity=3,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p0')
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource(),
                                   quantity=1,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p0')
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource(),
                                   quantity=4,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p1')
    self.createTransformedResource(transformation=transformation,
                                   resource_value=resource(),
                                   quantity=1,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/p1')
    return transformation

  def createBusinessProcess1(self, node_p0=None):
    """ order      p0      s0      p1     deliver
       ------- S0 ---- S1 ---- S2 ---- S3 ------- S4
         PO        PR     PPL      PR       PPL
    """
    business_process = self._createDocument("Business Process")
    builder = 'portal_deliveries/production_packing_list_builder'
    completed = 'delivered', 'started', 'stopped'
    phase_list = [('default/order', None, ('confirmed',)),
                  ('default/delivery', builder, completed)]
    phase_list[1:1] = [('mrp/p' + str(i),
                        'portal_deliveries/production_report_builder',
                        completed)
                       for i in xrange(2)]
    if node_p0 is not None:
      phase_list.insert(2, ('mrp/s0', builder, completed))
    predecessor = None
    for i, (phase, builder, completed) in enumerate(phase_list):
      successor = 'trade_state/s' + str(i)
      self.createBusinessLink(business_process,
                              completed_state=completed,
                              predecessor=predecessor,
                              successor=successor,
                              trade_phase=phase,
                              delivery_builder=builder)
      predecessor = successor
    phase_list = [x[0] for x in phase_list]
    if node_p0 is not None:
      self.createTradeModelPath(business_process,
                                destination_value=node_p0,
                                trade_phase=phase_list.pop(1))
      self.createTradeModelPath(business_process,
                                test_tales_expression="here/getSource",
                                trade_phase=phase_list.pop(1))
    self.createTradeModelPath(business_process, trade_phase_list=phase_list)
    return business_process

  def checkStock(self, resource, *node_variation_quantity):
    if isinstance(resource, str):
      resource = self.portal.unrestrictedTraverse(resource)
    expected_dict = dict(((x[0].getUid(), x[1]), x[2])
      for x in node_variation_quantity)
    for r in resource.getCurrentInventoryList(group_by_node=1,
                                              group_by_variation=1):
      self.assertEqual(expected_dict.pop((r.node_uid, r.variation_text), 0),
                       r.inventory)
    self.assertFalse(any(expected_dict.itervalues()), expected_dict)

class TestMRPImplementation(TestMRPMixin):
  """the test for implementation"""

  def test(self):
    workshop = self.createNode(title='workshop')
    workshop2 = self.createNode(title='workshop2')
    destination = self.createNode(title='destination')
    business_process = self.createBusinessProcess1(workshop2)
    order = self.createDefaultOrder(business_process)
    order_line, = order.objectValues()
    order._edit(source_value=workshop, destination_value=destination)
    self.tic()

    order.plan()
    self.tic()

    ar, = order.getCausalityRelatedValueList(portal_type="Applied Rule")
    sm, = ar.objectValues() # order
    ar, = sm.objectValues()
    sm, = ar.objectValues() # deliver
    ar, = sm.objectValues()

    movement_list = []
    resource = order_line.getResource()
    for sm in ar.objectValues():
      self.assertEqual(sm.getSource(), None)
      self.assertTrue(sm.getDestination())
      # Reference is used to match movements when reexpanding.
      reference = sm.getReference()
      if reference.split('/', 1)[0] in ('pr', 'cr'):
        self.assertEqual(sm.getResource(), resource)
      else:
        cr = self.portal.unrestrictedTraverse(reference).getResource()
        self.assertTrue(None != sm.getResource() == cr != resource)
        reference = None
      movement_list.append((sm.getTradePhase(), sm.getQuantity(),
                            reference, sm.getIndustrialPhaseList()))
    movement_list.sort()
    self.assertEqual(movement_list, sorted((
      ('mrp/p0', -10, None, []),
      ('mrp/p0', -30, None, []),
      ('mrp/p0', 10, 'pr/mrp/p0', ['trade_phase/mrp/p0']),
      ('mrp/p1', -10, 'cr/mrp/p1', ['trade_phase/mrp/p0']),
      ('mrp/p1', -10, None, []),
      ('mrp/p1', -40, None, []),
      ('mrp/p1', 10, 'pr', []),
      )))

    order.confirm()
    order.localBuild()
    self.tic()
    self.checkStock(resource)

    def getRelatedDeliveryList(portal_type):
      return order.getCausalityRelatedValueList(portal_type=portal_type)

    pr1, = getRelatedDeliveryList("Production Report")
    pr1.start()
    pr1.deliver()
    order.localBuild()
    self.tic()
    variation = 'industrial_phase/trade_phase/mrp/p0'
    self.checkStock(resource, (workshop2, variation, 10))

    ppl1, = getRelatedDeliveryList("Production Packing List")
    ppl1.start()
    ppl1.deliver()
    order.localBuild()
    self.tic()
    self.checkStock(resource, (workshop, variation, 10))

    pr2, = (x for x in getRelatedDeliveryList("Production Report")
              if x.aq_base is not pr1.aq_base)
    pr2.start()
    pr2.deliver()
    order.localBuild()
    self.tic()
    self.checkStock(resource, (workshop, '', 10))

    ppl2, = (x for x in getRelatedDeliveryList("Production Packing List")
               if x.aq_base is not ppl1.aq_base)
    ppl2.start()
    ppl2.deliver()
    self.tic()
    self.checkStock(resource, (destination, '', 10))


def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestMRPImplementation))
  return suite
