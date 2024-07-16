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
from erp5.component.test.testBPMCore import TestBPMMixin
from six.moves import range

class TestMRPMixin(TestBPMMixin):

  def afterSetUp(self):
    super(TestMRPMixin, self).afterSetUp()
    self._createRule("Transformation Simulation Rule")
    production_simulation_rule = self._createRule("Production Simulation Rule")
    production_simulation_rule.setTradePhase("manufacturing/order")
    rule = self._createRule("Transformation Sourcing Simulation Rule")
    rule._setSameTotalQuantity(False)

  def getBusinessTemplateList(self):
    return TestBPMMixin.getBusinessTemplateList(self) + ('erp5_mrp', )

  def _createRule(self, portal_type):
    x = portal_type.replace(' Simulation ', ' ').replace(' ', '_').lower()
    reference = "default_" + x
    id_ = "testMRP_" + x
    rule_tool = self.portal.portal_rules
    try:
      rule = self.getRule(reference=reference)
      self.assertEqual(rule.getId(), id_)
    except IndexError:
      rule = rule_tool.newContent(id_, portal_type,
        reference=reference,
        test_method_id="SimulationMovement_test" + portal_type.replace(' ', ''))
      def newTester(p, t, **kw):
        kw.setdefault("tested_property", p)
        return rule.newContent(id=p  + "_tester", portal_type=t + " Divergence Tester",
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
        ('manufacturing_step_' + str(i) for i in range(2)))
    self.createCategoriesInCategory(category_tool.trade_phase.mrp,
        ('sourcing_' + str(i) for i in range(1)))
    self.createCategoriesInCategory(category_tool.trade_state,
        ('step_' + str(i) for i in range(6)))

  def createDefaultOrder(self, business_process, transformation=None):
    if transformation is None:
      transformation = self.createDefaultTransformation()
    base_date = DateTime()
    order = self.createOrder(specialise_value=business_process,
                             start_date=base_date,
                             stop_date=base_date+3)
    self.createOrderLine(order,
                         quantity=10,
                         resource=transformation.getResource(),
                         specialise_value=transformation)
    return order

  def createDefaultTransformation(self):
    resource = lambda: self.createProduct(quantity_unit_list=['weight/kg'])
    self.produced_resource = resource()
    transformation = self.createTransformation(resource_value=self.produced_resource)
    self.consumed_resource_1 = resource()
    self.createTransformedResource(transformation=transformation,
                                   resource_value=self.consumed_resource_1,
                                   quantity=3,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/manufacturing_step_0')
    self.consumed_resource_2 = resource()
    self.createTransformedResource(transformation=transformation,
                                   resource_value=self.consumed_resource_2,
                                   quantity=1,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/manufacturing_step_0')
    self.consumed_resource_3 = resource()
    self.createTransformedResource(transformation=transformation,
                                   resource_value=self.consumed_resource_3,
                                   quantity=4,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/manufacturing_step_1')
    self.consumed_resource_4 = resource()
    self.createTransformedResource(transformation=transformation,
                                   resource_value=self.consumed_resource_4,
                                   quantity=1,
                                   quantity_unit_list=['weight/kg'],
                                   trade_phase='mrp/manufacturing_step_1')
    return transformation

  def createBusinessProcess1(self, node_p0):
    """
    Terms
    =====
    PO  : Production Order
      Used to Order the delivery of a final product from a workshop
    PPL : Production Packing List
      Production Packing List is used to deliver the final product
      from the Workshop
    MO  : Manufacturing Order
      Used to Order the manufacturing of a product. The Transformation defines
      the list of products and services needed to manufacture the final product
    ME  : Manufacturing Execution
      Oversees the Manufacturing Process on workshop, it is responsible for
      the movement of product and services consumption
    IPL : Internal Packing List
      Used to moves parts inside the factory.

    Context
    =======
    The transformation used in this business process is split into two part,
    this is configured by using transformed resource lines with different
    trade phases.

    Business Process
    ================
    The Business process will proceed this way:
    1/ Generate Production Order and confirm it
    2/ Generate Manufacturing Order and confirm it
    2/ Generate Manufacturing Execution manufacturing_step_0 which generate a
      the product with a variation to indicate it is a partial product.
      The variation is trade_phase/mrp/manufacturing_step_0. It takes place in workshop2
    3/ Delivering the first Manufacturing Execution leads to the build
      of a Internal Packing List to move the delivered half built product
      from "workshop2" to "workshop" the next fabrication line.
    4/ Delivering the IPL will build the second Manufacturing Execution
      manufacturing_step_1 which takes as input the variated expected product
      and resource 3 and 4.
      It takes place in "workshop" node
    5/ Delivering p1 will build the last production packing List with source
      "workshop" and destination "destination"

    Business Process Schema
    =======================
        order          order       manufacturing_step_0       sourcing_0
       ------- step_0 ----- step_1 -------------------- step_2 -------- step_3 -->
         PO             MO              ME1                      IPL

                  manufacturing_step_1        deliver
        --> step_3 ------------------- step_4 -------- step_5
                        ME2                     PPL
    Simulation Tree
    ===============
    * PO / new_order_root_simulation_rule
      * Production Order Line
        * default_delivering_rule
          * PPL
            * default_production_rule
              * MO
                * default_transformation_rule
                  * input ME1
                  * input ME1
                  * output ME1 - partial product
                  * input ME2 - partial product
                    * default_transformation_source_rule
                      * IPL
                  * input ME2
                    * default_transformation_source_rule
                  * input ME2
                    * default_transformation_source_rule
                  * output ME2
    """
    business_process = self._createDocument("Business Process")
    production_packing_list_builder = 'portal_deliveries/production_packing_list_builder'
    manufacturing_execution_builder = 'portal_deliveries/manufacturing_execution_builder'
    manufacturing_order_builder = 'portal_deliveries/manufacturing_order_builder'
    sourcing_builder = 'portal_deliveries/transformation_sourcing_internal_packing_list_builder'
    completed = 'delivered', 'started', 'stopped'
    phase_list = [
      ('trade/order', None, ('confirmed',)),
      ('manufacturing/order', manufacturing_order_builder, ('confirmed',)),
      ('mrp/manufacturing_step_0', manufacturing_execution_builder, completed),
      ('mrp/sourcing_0', sourcing_builder, completed),
      ('mrp/manufacturing_step_1', manufacturing_execution_builder, completed),
      ('trade/delivery', production_packing_list_builder, completed)
    ]
    predecessor = None
    for i, (phase, builder, completed) in enumerate(phase_list):
      successor = 'trade_state/step_' + str(i)
      self.createBusinessLink(business_process,
                              completed_state=completed,
                              predecessor=predecessor,
                              successor=successor,
                              trade_phase=phase,
                              delivery_builder=builder)
      predecessor = successor
    phase_list = [x[0] for x in phase_list]
    self.createTradeModelPath(business_process,
                              destination_value=node_p0,
                              trade_phase=phase_list.pop(2))
    self.createTradeModelPath(business_process,
                              test_tales_expression="here/getSource",
                              trade_phase=phase_list.pop(2))
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

  def createMRPOrder(self, use_item=False):
    self.workshop = self.createNode(title='workshop')
    self.workshop2 = self.createNode(title='workshop2')
    self.destination = self.createNode(title='destination')
    business_process = self.createBusinessProcess1(self.workshop2)
    self.order = self.createDefaultOrder(business_process)
    self.order_line, = self.order.objectValues()
    if use_item:
      self.item = self.portal.item_module.newContent()
      self.order_line.setAggregateValue(self.item)
    self.order._edit(source_value=self.workshop, destination_value=self.destination)
    self.order.plan()
    self.tic()

  def testSimpleOrder(self):
    """
    We test the process implemented in 'createBusinessProcess1' is
    correctly followed
    """
    self.createMRPOrder()
    order = self.order

    # new_order_root_simulation_rule
    ar, = order.getCausalityRelatedValueList(portal_type="Applied Rule")
    # Production Order Line
    sm, = ar.objectValues()
    # default_delivering_rule
    ar, = sm.objectValues()
    # The final PPL
    sm, = ar.objectValues() # deliver
    # default_production_rule
    ar, = sm.objectValues()
    # Manufacturing Order Movements
    sm, = ar.objectValues() # Order
    # default_transformation_rule
    ar, = sm.objectValues()

    movement_list = []
    resource = self.order_line.getResource()
    # This is the list of movement generated by the transformation rule.
    for sm in ar.objectValues():
      self.assertEqual(sm.getSource(), None)
      self.assertTrue(sm.getDestination())
      # Reference is used to match movements when reexpanding.
      reference = sm.getReference()
      # Theses are the intermediary movement
      if reference.split('/', 1)[0] in ('pr', 'cr'):
        self.assertEqual(sm.getResource(), resource)
      else:
        # The reference is the transformation line, so we assert the resource
        # of the movement is the same as the corresponding line.
        cr = self.portal.unrestrictedTraverse(reference).getResource()
        self.assertTrue(None != sm.getResource() == cr != resource)
        reference = None
      movement_list.append((sm.getTradePhase(), sm.getQuantity(),
                            reference, sm.getIndustrialPhaseList()))
    movement_list.sort()
    self.assertEqual(movement_list, sorted((
      ('mrp/manufacturing_step_0', -10.0, None, []),
      ('mrp/manufacturing_step_0', -30.0, None, []),
      ('mrp/manufacturing_step_0', 10.0,
       'pr/mrp/manufacturing_step_0', ['trade_phase/mrp/manufacturing_step_0']),
      ('mrp/manufacturing_step_1', -10.0,
       'cr/mrp/manufacturing_step_1', ['trade_phase/mrp/manufacturing_step_0']),
      ('mrp/manufacturing_step_1', -10.0, None, []),
      ('mrp/manufacturing_step_1', -40.0, None, []),
      ('mrp/manufacturing_step_1', 10.0, 'pr', []),
      )))

    order.confirm()
    # Build Manufacturing Order
    order.localBuild()
    self.tic()

    def getRelatedDeliveryList(portal_type):
      return order.getCausalityRelatedValueList(portal_type=portal_type)

    self.assertEqual(len(getRelatedDeliveryList("Manufacturing Order Line")), 1)
    # Build First Manufacturing Execution
    order.localBuild()
    self.tic()
    self.checkStock(resource)

    me1, = getRelatedDeliveryList("Manufacturing Execution")
    me1.start()
    me1.deliver()
    order.localBuild()
    self.tic()
    variation = 'industrial_phase/trade_phase/mrp/manufacturing_step_0'
    self.checkStock(resource, (self.workshop2, variation, 10))

    ipl, = getRelatedDeliveryList("Internal Packing List")
    ipl.start()
    ipl.deliver()
    order.localBuild()
    self.tic()
    self.checkStock(resource, (self.workshop, variation, 10))

    me2, = (x for x in getRelatedDeliveryList("Manufacturing Execution")
              if x.aq_base is not me1.aq_base)
    me2.start()
    me2.deliver()
    order.localBuild()
    self.tic()
    self.checkStock(resource, (self.workshop, '', 10))

    ppl, = (x for x in getRelatedDeliveryList("Production Packing List")
               if x.aq_base is not ipl.aq_base)
    ppl.start()
    ppl.deliver()
    self.tic()
    self.checkStock(resource, (self.destination, '', 10))

  def checkExpectedLineList(self, delivery, expected_line_list):
    found_line_list = []
    for line in delivery.getMovementList():
      found_line_list.append((line.getResourceValue(), line.getQuantity(),
                              line.getAggregateValue()))
    sortKey = lambda x: x[0].getRelativeUrl()
    found_line_list.sort(key=sortKey)
    expected_line_list.sort(key=sortKey)
    self.assertEqual(expected_line_list, found_line_list)

  def testOrderWithItem(self):
    """
    Check item propagation from Production Order to Manufacturing Execution
    and Production Packing List
    """
    self.createMRPOrder(use_item=True)
    order = self.order
    order.confirm()
    order.localBuild()
    self.tic()
    manufacturing_order_line, = order.getCausalityRelatedValueList(
                            portal_type="Manufacturing Order Line")
    self.assertEqual(self.item, manufacturing_order_line.getAggregateValue())
    order.localBuild()
    self.tic()

    manufacturing_execution, = order.getCausalityRelatedValueList(
                                portal_type="Manufacturing Execution")
    #                        resource,            quantity, item
    expected_line_list = [(self.produced_resource, 10.0, self.item),
                          (self.consumed_resource_1, -30.0, None),
                          (self.consumed_resource_2, -10.0, None)]
    self.checkExpectedLineList(manufacturing_execution, expected_line_list)

  def _test_add_and_clone_tranformed_resource(self, portal_type):
    test_product = self.portal.product_module.newContent()

    transformation = self.portal.transformation_module.newContent(
        portal_type='Transformation',
        reference='TR1',
        resource_value=test_product)

    transformed_resource = transformation.newContent(
        portal_type=portal_type)

    # transformation transformed resource is initialised with int index
    self.assertEqual(1, transformed_resource.getIntIndex())

    transformed_resource_2 = transformation.newContent(
        portal_type=portal_type)
    # int index increments as the number of lines increase
    self.assertEqual(2, transformed_resource_2.getIntIndex())
    transformed_resource_2.setReference('user defined reference')

    # when cloning a transformation transformed resource, int index is also
    # cloned and not incremented.
    transformed_resource_3 = transformed_resource_2.Base_createCloneDocument(batch_mode=True)
    self.assertEqual(2, transformed_resource_3.getIntIndex())
    self.assertEqual('user defined reference', transformed_resource_3.getReference())

    # Cloning a transformation properly keep the transformation transformed resources references
    transformed_resource_2.setIntIndex(123)
    transformation_2 = transformation.Base_createCloneDocument(batch_mode=True)
    self.assertEqual(1, transformation_2['1'].getIntIndex())
    self.assertEqual(123, transformation_2['2'].getIntIndex())
    self.assertEqual(2, transformation_2['3'].getIntIndex())

    self.assertEqual('user defined reference', transformation_2['2'].getReference())

  def test_add_and_clone_transformation_transformed_resource(self):
    self._test_add_and_clone_tranformed_resource('Transformation Transformed Resource')

  def test_add_and_clone_transformation_optional_resource(self):
    self._test_add_and_clone_tranformed_resource('Transformation Optional Resource')

  def test_add_and_clone_transformation_operation(self):
    self._test_add_and_clone_tranformed_resource('Transformation Operation')

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestMRPImplementation))
  return suite
