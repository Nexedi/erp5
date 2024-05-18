##############################################################################
#
# Copyright (c) 2005-2008 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Romain Courteaud <romain@nexedi.com>
#          Lukasz Nowak <lukasz.nowak@ventis.com.pl>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
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
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from erp5.component.test.testOrder import TestOrderMixin
from Products.ERP5.tests.utils import newSimulationExpectedFailure

class TestProductionOrderMixin(TestOrderMixin):

  run_all_test = 1
  resource_portal_type = 'Product'
  order_portal_type = 'Production Order'
  order_line_portal_type = 'Production Order Line'
  order_cell_portal_type = 'Production Order Cell'
  supply_chain_portal_type = 'Supply Chain'
  supply_node_portal_type = 'Supply Node'
  supply_link_portal_type = 'Supply Link'
  component_portal_type = 'Component'
  transformation_portal_type = 'Transformation'
  transformed_resource_portal_type = \
                        'Transformation Transformed Resource'
  operation_line_portal_type = 'Transformation Operation'

  operation_category_list = ['operation1', 'operation2']
  colour_variation_portal_type = 'Product Individual Variation'
  morphology_variation_portal_type = 'Product Individual Variation'

  colour_list = ['green','blue']
  mrp_size_list = ['Man','Woman']


  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_simulation', 'erp5_trade', 'erp5_mrp',
            'erp5_simulation_test')

  def setUpPreferences(self):
    system_preference = self.portal.portal_preferences.newContent(
      portal_type = 'System Preference'
    )
    system_preference.edit(
      preferred_product_individual_variation_base_category = ('variation',),
      preferred_component_individual_variation_base_category = ('variation',),
      preferred_product_variation_base_category = ('industrial_phase', 'colour', 'size'),
      preferred_component_variation_base_category = ('colour', 'size'),
      priority = 1,
    )
    system_preference.enable()
    self.tic()

  def afterSetUp(self):
    TestOrderMixin.afterSetUp(self)
    self.loginByUserName('manager')
    self.setUpPreferences()
    self.loginByUserName('test_user')

  def createCategories(self):
    """
      Light install create only base categories, so we create
      some categories for testing them
    """
    TestOrderMixin.createCategories(self)
    if len(self.category_tool.operation.contentValues()) == 0:
      for category_id in self.operation_category_list:
        self.category_tool.operation.newContent(portal_type='Category',
                                                id=category_id)

  def stepCreateColourSizeVariatedComponent1(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource with colour and size variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.component_portal_type)
    resource = resource_module.newContent(
                                  portal_type=self.component_portal_type)
    resource.edit(
      title = "ColourSizeVariatedComponent1",
      variation_base_category_list = ['colour','size'],
    )
    resource.setVariationCategoryList(['size/'+q for q in self.mrp_size_list] + ['colour/'+q for q in self.colour_list])
    sequence.edit(component1=resource)

  def stepCreateColourSizeVariatedResource(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with colour and size variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "ColourSizeVariatedResource",
      industrial_phase_list=["phase1", "phase2"],
      variation_base_category_list = ['size','colour'],
    )
    resource.setVariationCategoryList(['size/'+q for q in self.mrp_size_list] + ['colour/'+q for q in self.colour_list])

    sequence.edit( resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  def stepCreateVariatedResource(self, sequence=None, sequence_list=None, \
                                 **kw):
    """
      Create a resource with variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.resource_portal_type)
    resource = resource_module.newContent(portal_type=self.resource_portal_type)
    resource.edit(
      title = "VariatedResource",
      industrial_phase_list=["phase1", "phase2"],
      product_line = 'apparel'
    )
#    resource.setSizeList(self.size_list)
    # Add colour variation

    colour_variation_count = 3
    for i in range(colour_variation_count):
      variation = resource.newContent(portal_type = self.colour_variation_portal_type)
      variation.edit(
        title = 'ColourVariation%s' % str(i),
        variation_base_category_list = ('variation',)
      )
    # Add morphology variation
    morphology_variation_count = 2
    for i in range(morphology_variation_count) :
      variation = resource.newContent(portal_type=self.morphology_variation_portal_type)
      variation.edit(
        title = 'MorphologyVariation%s' % str(i),
        variation_base_category_list = ('variation',)
      )

    sequence.edit( resource = resource )
    resource_list = sequence.get('resource_list',default=[])
    resource_list.append(resource)
    sequence.edit( resource_list = resource_list )

  def stepCreateProductionOrganisation1(self, sequence=None, sequence_list=None,
                                        **kw):
    """
      Create a organisation for supply
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                title='production_organisation1', **kw)

  # Note: SC means Supply Chain
  def stepCreateGenericSC(self, sequence=None, sequence_list=None, **kw):
    """
      Create a empty Supply Chain
    """
    portal = self.getPortal()
    supply_chain_module = portal.getDefaultModule( \
                                   portal_type=self.supply_chain_portal_type)
    supply_chain = supply_chain_module.newContent( \
                                   portal_type=self.supply_chain_portal_type)
    supply_chain.edit(
      title = "Supply Chain Generic",
    )
    sequence.edit(supply_chain=supply_chain)

  def stepCreateProductionSC(self, sequence=None, sequence_list=None,
                             **kw):
    """
      Create a empty organisation
    """
    # Create supply chain
    self.stepCreateGenericSC(sequence=sequence, sequence_list=sequence_list,
                             **kw)
    supply_chain = sequence.get('supply_chain')
    supply_chain.edit(
      title = 'Supply Chain Production'
    )
    # Create production node
    production_organisation  = sequence.get('production_organisation1')
    production_node = supply_chain.newContent(
                         portal_type=self.supply_node_portal_type)
    production_node.edit(
      destination_value=production_organisation
    )
    sequence.edit(production_node1=production_node)
    # Create production link
    production_link = supply_chain.newContent(
                         portal_type=self.supply_link_portal_type)
    production_link.edit(
      destination_value=production_node,
      destination_section_value=production_organisation,
      min_delay=5,
      max_delay=6,
      deliverable=1,
      industrial_phase_list=["phase1"]
    )

  def stepCreateComponent1(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.component_portal_type)
    resource = resource_module.newContent(
                                  portal_type=self.component_portal_type)
    resource.edit(
      title = "Component1"
    )
    sequence.edit(component1=resource)

  def stepCreateComponent2(self,sequence=None, sequence_list=None, \
                                    **kw):
    """
      Create a resource with no variation
    """
    portal = self.getPortal()
    resource_module = portal.getDefaultModule(self.component_portal_type)
    resource = resource_module.newContent(
                                  portal_type=self.component_portal_type)
    resource.edit(
      title = "Component2"
    )
    sequence.edit(component2=resource)

  def stepInvalidateTransformation(self, sequence=None, sequence_list=None,
                               **kw):
    transformation = sequence.get('transformation')

    workflow_tool = self.getPortal().portal_workflow

    workflow_tool.doActionFor(
        transformation,
        'invalidate_action'
    )

    self.assertEqual('invalidated',transformation.getValidationState())

  def stepValidateTransformation(self, sequence=None, sequence_list=None,
                               **kw):
    transformation = sequence.get('transformation')

    workflow_tool = self.getPortal().portal_workflow

    workflow_tool.doActionFor(
        transformation,
        'validate_action'
    )

    self.assertEqual('validated',transformation.getValidationState())

  def stepCreateEmptyTransformation(self, sequence=None, sequence_list=None,
                               **kw):
    portal = self.getPortal()
    transformation_module = portal.getDefaultModule(
                                     self.transformation_portal_type)
    transformation = transformation_module.newContent(
                                   portal_type=self.transformation_portal_type)
    sequence.edit(transformation=transformation)


  def stepSetTransformationTransformedResourceQuantityMatrix(self, sequence=None, sequence_list=None,
                               **kw):
    """
      Fills variation based quantity matrix
    """

    transformation_transformed_resource = sequence.get('transformation_transformed_resource')

    for colour in self.colour_list:
      colour_path = 'colour/%s' % colour
      for size in self.mrp_size_list:
        size_path = 'size/%s' % size
        transformation_transformed_resource.newCell(
          colour_path,
          size_path,
          mapped_value_property_list = ('quantity',),
          quantity = self.colour_size_quantity_dict[colour][size],
          membership_criterion_base_category= ('size', 'colour', ),
          membership_criterion_category= (size_path, colour_path,),
          base_id="quantity",
        )

  def stepSetTransformationTransformedResourceVariationMatrix(self, sequence=None, sequence_list=None,
                               **kw):
    """
      Fills variation matrix
    """

    transformation_transformed_resource = sequence.get('transformation_transformed_resource')

    for colour in self.colour_list:
      colour_path = 'colour/%s' % colour
      for size in self.mrp_size_list:
        size_path = 'size/%s' % size
        transformation_transformed_resource.newCell(
          colour_path,
          size_path,
          categories = self.colour_size_variation_dict[colour][size],
          membership_criterion_base_category= ('size', 'colour', ),
          membership_criterion_category= (size_path, colour_path,),
          base_id="variation",
        )

  def stepSetOrderLineQuantityMatrix(self, sequence=None, sequence_list=None,
                               **kw):
    """
      Fills variation based quantity matrix
    """
    order_line = sequence.get('order_line')

    for colour in self.colour_list:
      colour_path = 'colour/%s' % colour
      for size in self.mrp_size_list:
        size_path = 'size/%s' % size
        order_line.newCell(
          size_path,
          colour_path,
          mapped_value_property_list = ('quantity',),
          quantity = self.order_line_colour_size_quantity_dict[colour][size],
          categories = [size_path, colour_path],
          membership_criterion_base_category= ('size', 'colour', ),
          membership_criterion_category= (size_path, colour_path,),
          base_id='movement',
        )

  def stepSetOrderLineVariationCategories(self, sequence=None, sequence_list=None,
                               **kw):
    order_line = sequence.get('order_line')

    order_line.setVariationCategoryList(
      value = self.order_line_variation_category_list
    )

  def stepSetTransformationTransformedResourceVariation(self, sequence=None, sequence_list=None,
                               **kw):
    """
      Fills categories of variation
    """

    transformation_transformed_resource = sequence.get('transformation_transformed_resource')

    transformation_transformed_resource.edit(
        v_variation_base_category_list = self.variation_category_list,
        q_variation_base_category_list = self.variation_category_list,
    )

  def stepSetTransformationVariation(self, sequence=None, sequence_list=None,
                               **kw):
    """
      Fills categories of variation
    """
    transformation = sequence.get('transformation')
    transformation.setVariationBaseCategoryList(self.variation_category_list)

  def stepFillTransformationWithResource(self, sequence=None, sequence_list=None,
                               **kw):

    transformation = sequence.get('transformation')
    resource = sequence.get('resource')
    self.assertNotEqual(None, resource)
    transformation.setResourceValue(resource)

  def stepSetOrderLineQuantity(self, sequence=None, sequence_list=None,
                               **kw):
    order_line = sequence.get('order_line')
    order_line.edit(
        quantity = self.production_order_line_quantity
    )

  def stepSetTransformationTransformedResourceQuantity(self, sequence=None, sequence_list=None,
                               **kw):
    transformation_transformed_resource = sequence.get('transformation_transformed_resource')
    transformation_transformed_resource.edit(
      quantity = self.transformation_transformed_resource_quantity
    )

  def stepSetTransformationTransformedResourceEfficiency(self, sequence=None, sequence_list=None,
                               **kw):
    transformation_transformed_resource = sequence.get('transformation_transformed_resource')
    transformation_transformed_resource.edit(
      efficiency = self.transformation_transformed_resource_efficiency
    )

  def stepSetTransformationTransformedResourceIndustrialPhaseList(self, sequence=None, sequence_list=None,
                               **kw):
    transformation_transformed_resource = sequence.get('transformation_transformed_resource')
    transformation_transformed_resource.edit(
      industrial_phase_list = self.transformation_transformed_resource_industrial_phase_list
    )

  def stepFillTransformationTransformedResourceWithComponent1(self, sequence=None, sequence_list=None,
                               **kw):
    transformation_transformed_resource = sequence.get('transformation_transformed_resource')
    component1 = sequence.get('component1')

    self.assertNotEqual(None, component1)

    transformation_transformed_resource.edit(
      resource_value = component1,
    )

  def stepCreateTransformationTransformedResource(self, sequence=None, sequence_list=None,
                               **kw):

    transformation = sequence.get('transformation')
    transformation_transformed_resource = transformation.newContent(
      portal_type = self.transformed_resource_portal_type,
        )

    sequence.edit(transformation_transformed_resource = transformation_transformed_resource)

  def stepCreateTransformation(self, sequence=None, sequence_list=None,
                               **kw):
    """
      Create a transformation
    """
    # Create transformation
    portal = self.getPortal()
    transformation_module = portal.getDefaultModule(
                                     self.transformation_portal_type)
    transformation = transformation_module.newContent(
                                   portal_type=self.transformation_portal_type)
    sequence.edit(transformation=transformation)
    # Set resource
    resource = sequence.get('resource')
    transformation.setResourceValue(resource)
    # Create operation line 1
    operation_line = transformation.newContent(
        portal_type=self.operation_line_portal_type)
    operation_line.edit(
        # FIXME hardcoded
        quantity=2,
        resource_value=portal.portal_categories.resolveCategory(
                                     'operation/operation1'),
        industrial_phase_list=['phase1']
    )

    # Create operation line 2
    operation_line = transformation.newContent(
        portal_type=self.operation_line_portal_type)
    operation_line.edit(
        # FIXME hardcoded
        quantity=3,
        resource_value=portal.portal_categories.resolveCategory(
                                     'operation/operation2'),
        industrial_phase_list=['phase2']
    )
    # Create transformed resource line 1
    line = transformation.newContent(
        portal_type=self.transformed_resource_portal_type)
    line.edit(
        # FIXME hardcoded
        quantity=6,
        resource_value=sequence.get('component1'),
        industrial_phase_list=['supply_phase1']
    )
    # Create transformed resource line 2
    line = transformation.newContent(
        portal_type=self.transformed_resource_portal_type)
    line.edit(
        # FIXME hardcoded
        quantity=7,
        resource_value=sequence.get('component2'),
        industrial_phase_list=['supply_phase2']
    )

  def stepCreateOrder(self, sequence=None, sequence_list=None, **kw):
    """
      Create a filled order
    """
    portal = self.getPortal()
    order_module = portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type)
    organisation = sequence.get('organisation')
    supply_chain = sequence.get('supply_chain')
    order.edit(
      start_date = self.datetime + 10,
      stop_date = self.datetime + 20,
      destination_value=organisation,
      destination_section_value=organisation,
      specialise_value=supply_chain
    )
    sequence.edit(order=order)

  def stepCreateOrderLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create a filled order line
    """
    order = sequence.get('order')
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    resource = sequence.get('resource')
    transformation = sequence.get('transformation')
    order_line.edit(
      resource_value=resource,
      specialise_value=transformation,
      quantity=5
    )
    sequence.edit(order_line=order_line)

  def stepCreateOrderLineWithoutTransformation(self, sequence=None, sequence_list=None, **kw):
    """
      Create a empty order line
    """
    order = sequence.get('order')
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    resource = sequence.get('resource')
    order_line.edit(
      resource_value=resource,
      quantity=5
    )
    sequence.edit(order_line=order_line)

  def stepCheckVariationSimulation(self, sequence=None, sequence_list=None, **kw):
    # XXX: This check is not testing too much, beside for variation system
    #      used in production simulations.
    order = sequence.get('order')

    movement_list = order.getMovementList()
    self.assertNotEqual(len(movement_list), 0)

    for order_movement in movement_list:
      size = order_movement.getSize()
      colour = order_movement.getColour()

      self.assertNotEqual(size, None)
      self.assertNotEqual(colour, None)

      want_produced_quantity = self.order_line_colour_size_quantity_dict[colour][size]
      want_consume_quantity = self.colour_size_quantity_dict[colour][size]
      want_consume_for_production = want_produced_quantity * want_consume_quantity

      order_simulation_movement = order_movement.getDeliveryRelatedValue(\
          portal_type='Simulation Movement')
      produced_movement = order_simulation_movement.contentValues()[0].contentValues()[0]

      self.assertEqual(
        want_produced_quantity,
        produced_movement.getQuantity()
      )

      transformation_rule = produced_movement.contentValues()[0]

      consumption_movement = [q for q in transformation_rule.contentValues() \
          if q.getId().startswith('cr')][0]
      production_delivery_movement = [q for q in transformation_rule.contentValues() \
          if q.getId().startswith('pr')][0]

      self.assertEqual(
          want_consume_for_production,
          consumption_movement.getQuantity()
      )

      self.assertEqual(
        want_produced_quantity,
        production_delivery_movement.getQuantity()
      )

      transformation_sourcing_rule = consumption_movement.contentValues()[0]

      consume_delivery_movement = transformation_sourcing_rule.contentValues()[0]

      self.assertEqual(
        want_consume_for_production,
        consume_delivery_movement.getQuantity()
      )

  def stepCheckEfficiencySimulation(self, sequence=None, sequence_list=None, **kw):
    """Check that efficiency is applied where is it needed"""

    # XXX: This check is not testing too much, beside for efficiency related quantity
    #      in just two places.
    order = sequence.get('order')

    applied_rule = order.getCausalityRelatedValue(portal_type = self.applied_rule_portal_type)

    order_simulation_movement_list = applied_rule.contentValues()

    # XXX: hardcode
    self.assertEqual(
        1,
        len(order_simulation_movement_list)
    )

    order_simulation_movement = order_simulation_movement_list[0]
    production_applied_rule = order_simulation_movement.contentValues()[0]
    production_movement_list = production_applied_rule.contentValues()
    production_movement = production_movement_list[0]

    transformation_applied_rule = production_movement.contentValues()[0]

    consumed_movement = [q for q in transformation_applied_rule.contentValues() \
        if q.getId().startswith('cr')][0]

    self.assertEqual(
        consumed_movement.getQuantity(),
        self.quantity_after_efficiency_calculation
    )

    transformation_sourcing_rule = consumed_movement.contentValues()[0]

    consumption_delivery_movement = [q for q in transformation_sourcing_rule.contentValues() \
        if q.getId().startswith('ts')][0]

    self.assertEqual(
        consumption_delivery_movement.getQuantity(),
        self.quantity_after_efficiency_calculation
    )

  def stepCheckOrderLineTransformationIsSet(self, sequence=None, sequence_list=None, **kw):
    order_line = sequence.get('order_line')
    transformation = sequence.get('transformation')

    self.assertNotEqual(None, transformation)

    self.assertEqual(order_line.getSpecialiseValue(), transformation)

  def stepCheckOrderLineTransformationIsNotSet(self, sequence=None, sequence_list=None, **kw):
    order_line = sequence.get('order_line')

    self.assertEqual(order_line.getSpecialiseValue(), None)

  def stepRemoveResourceFromOrderLine(self, sequence=None, sequence_list=None, **kw):
    order_line = sequence.get('order_line')

    order_line.edit(
        resource = None
    )

  def stepCheckOrderSimulation(self, sequence=None, sequence_list=None, **kw):
    """
      Test if simulation is matching order
    """
    order = sequence.get('order')
    related_applied_rule_list = order.getCausalityRelatedValueList( \
                                   portal_type=self.applied_rule_portal_type)
    no_applied_rule_state = ('draft', 'auto_planned')
    order_state = order.getSimulationState()
    if order_state in no_applied_rule_state:
      self.assertEqual(0, len(related_applied_rule_list))
    else:
      self.assertEqual(1, len(related_applied_rule_list))
      applied_rule = related_applied_rule_list[0].getObject()
      sequence.edit(applied_rule=applied_rule)
      self.assertTrue(applied_rule is not None)
      # Test if applied rule has a specialise value with default_order_rule
      # XXX hardcoded value
      self.assertEqual('default_production_order_rule', \
                        applied_rule.getSpecialiseReference())

      simulation_movement_list = applied_rule.objectValues()
      sequence.edit(simulation_movement_list=simulation_movement_list)

  def checkObjectAttributes(self, obj, attribute_list):
    LOG('checkObjectAttributes object.getPath',0,obj.getPath())
    for value, attribute in attribute_list:
      try:
        self.assertEqual(value,
                          getattr(object, attribute)())
      except AssertionError:
        LOG('Raise Assertion error',0,'')
        LOG('object.getQuantity()',0,object.getQuantity())
        LOG('object.__dict__',0,object.__dict__)
        delivery_value = object.getDeliveryValue()
        LOG('object.getDeliveryValue()', 0, delivery_value)
        if delivery_value is not None:
          LOG('object.getDeliveryValue().getQuantity()',0,delivery_value.getQuantity())
        raise AssertionError("Attribute: %s, Value: %s, Result: %s"
          % (attribute, value, getattr(object, attribute)()))

  def stepCheckProductionSimulation(self, sequence=None, sequence_list=None,
                                    **kw):
    """
      Hardcoded check
    """
    self.stepCheckOrderSimulation(sequence=sequence,
                                  sequence_list=sequence_list, **kw)
    # Test simulation movement generated related to order line
    simulation_movement_list = sequence.get('simulation_movement_list')
    self.assertEqual(1, len(simulation_movement_list))
    order_line = sequence.get('order_line')
    related_simulation_movement_list = order_line.getDeliveryRelatedValueList()
    self.assertEqual(1, len(related_simulation_movement_list))
    related_simulation_movement = related_simulation_movement_list[0]
    self.assertEqual(related_simulation_movement,
                      simulation_movement_list[0])
    production_organisation1 = sequence.get('production_organisation1')
    # XXX FIXME test date
    self.checkObjectAttributes(
           related_simulation_movement, (
             (order_line.getQuantity(), 'getQuantity'),
             (order_line.getResourceValue(), 'getResourceValue'),
             (order_line.getVariationCategoryList(),
              'getVariationCategoryList'),
             (order_line.getDestinationValue(), 'getDestinationValue'),
             (order_line.getDestinationSectionValue(),
              'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    # Test next applied rule
    applied_rule_list = related_simulation_movement.objectValues()
    self.assertEqual(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_delivering_rule', \
                      applied_rule.getSpecialiseReference())
    # Test next applied rule
    simulation_movement_list = applied_rule.objectValues()
    self.assertEqual(1, len(simulation_movement_list))
    simulation_movement = simulation_movement_list[0]
    applied_rule_list = simulation_movement.objectValues()
    self.assertEqual(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_rule', \
                      applied_rule.getSpecialiseReference())
    # Test deeper simulation
    simulation_movement_list = applied_rule.objectValues()
    self.assertEqual(2, len(simulation_movement_list))
    # Test consumed movement
    transformation = sequence.get('transformation')
    consumed_movement_id = 'cr_%s_1_%s' % (transformation.getId(),
                                           applied_rule.getParentId())
    consumed_movement = applied_rule[consumed_movement_id]
    operation_resource = consumed_movement.portal_categories.resolveCategory(
                                              'operation/operation1')
    # FIXME
    self.checkObjectAttributes(
           consumed_movement, (
             (10, 'getQuantity'),
             (operation_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    # Test produced resource
    produced_movement = applied_rule.pr
    resource = sequence.get('resource')
    production_organisation1 = sequence.get('production_organisation1')
    self.checkObjectAttributes(
           produced_movement, (
             (5, 'getQuantity'),
             (resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (production_organisation1, 'getDestinationValue'),
             (production_organisation1, 'getDestinationSectionValue'),
             (None, 'getSourceValue'),
             (None, 'getSourceSectionValue')))

  def stepCreateSupplyOrganisation1(self, sequence=None, sequence_list=None,
                                        **kw):
    """
      Create a organisation for supply
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                title='supply_organisation1', **kw)

  def stepCreateSourcingSC(self, sequence=None, sequence_list=None,
                             **kw):
    """
      Create a empty organisation
    """
    # Create supply chain
    self.stepCreateProductionSC(sequence=sequence, sequence_list=sequence_list,
                                **kw)
    supply_chain = sequence.get('supply_chain')
    supply_chain.edit(
      title = 'Supply Chain Sourcing',
    )
    # Create supply node
    supply_organisation  = sequence.get('supply_organisation1')
    supply_node = supply_chain.newContent(
                         portal_type=self.supply_node_portal_type)
    supply_node.edit(
      destination_value=supply_organisation
    )
    # Create sourcing link
    supply_link = supply_chain.newContent(
                         portal_type=self.supply_link_portal_type)
    production_node1 = sequence.get('production_node1')
    production_organisation1 = sequence.get('production_organisation1')
    supply_link.edit(
      source_value=supply_node,
      source_section_value=supply_organisation,
      destination_value=production_node1,
      destination_section_value=production_organisation1,
      min_delay=5,
      max_delay=6,
      deliverable=0,
      industrial_phase_list=["supply_phase1"]
    )

  def stepCheckSourcingSimulation(self, sequence=None, sequence_list=None,
                                  **kw):
    """
      Hardcoded check
    """
    self.stepCheckOrderSimulation(sequence=sequence,
                                  sequence_list=sequence_list, **kw)
    # Test simulation movement generated related to order line
    simulation_movement_list = sequence.get('simulation_movement_list')
    self.assertEqual(1, len(simulation_movement_list))
    order_line = sequence.get('order_line')
    related_simulation_movement_list = order_line.getDeliveryRelatedValueList()
    self.assertEqual(1, len(related_simulation_movement_list))
    related_simulation_movement = related_simulation_movement_list[0]
    self.assertEqual(related_simulation_movement,
                      simulation_movement_list[0])
    production_organisation1 = sequence.get('production_organisation1')
    # XXX FIXME test date
    self.checkObjectAttributes(
           related_simulation_movement, (
             (order_line.getQuantity(), 'getQuantity'),
             (order_line.getResourceValue(), 'getResourceValue'),
             (order_line.getVariationCategoryList(),
              'getVariationCategoryList'),
             (order_line.getDestinationValue(), 'getDestinationValue'),
             (order_line.getDestinationSectionValue(),
              'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    # Test next applied rule
    applied_rule_list = related_simulation_movement.objectValues()[0].objectValues()[0].objectValues()
    self.assertEqual(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_rule', \
                      applied_rule.getSpecialiseReference())
    # Test deeper simulation
    simulation_movement_list = list(applied_rule.objectValues())
    # FIXME
    self.assertEqual(3, len(simulation_movement_list))
    # Test produced resource
    produced_movement = applied_rule.pr
    resource = sequence.get('resource')
    production_organisation1 = sequence.get('production_organisation1')
    self.checkObjectAttributes(
           produced_movement, (
             (5, 'getQuantity'),
             (resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (production_organisation1, 'getDestinationValue'),
             (production_organisation1, 'getDestinationSectionValue'),
             (None, 'getSourceValue'),
             (None, 'getSourceSectionValue')))
    self.assertEqual(0, len(produced_movement.objectValues()))

    simulation_movement_list.remove(produced_movement)
    # All code before is a stupid copy (except movement count)
    # Test consumed movement
    operation_resource = resource.portal_categories.resolveCategory(
                                              'operation/operation1')
    component_resource = sequence.get('component1')
#     for consumed_movement in (applied_rule.cr_1, applied_rule.cr_2):
    operation_movement = component_movement = None
    for consumed_movement in simulation_movement_list:
      if consumed_movement.getResourceValue() == operation_resource:
        operation_movement = consumed_movement
      else:
        component_movement = consumed_movement
    # Check operation movement
    self.checkObjectAttributes(
           operation_movement, (
             (10, 'getQuantity'),
             (operation_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    self.assertEqual(0, len(operation_movement.objectValues()))
    # Check component movement
    self.checkObjectAttributes(
           component_movement, (
             (30, 'getQuantity'),
             (component_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    self.assertEqual(1, len(component_movement.objectValues()))
    # Test supply applied rule
    applied_rule = component_movement.objectValues()[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_sourcing_rule', \
                      applied_rule.getSpecialiseReference())
    # Test supply movement
    simulation_movement_list = applied_rule.objectValues()
    # FIXME
    self.assertEqual(1, len(simulation_movement_list))
    # Test supply resource
    supply_movement = applied_rule.ts
    supply_organisation1 = sequence.get('supply_organisation1')
    self.checkObjectAttributes(
           supply_movement, (
             (30, 'getQuantity'),
             (component_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (production_organisation1, 'getDestinationValue'),
             (production_organisation1, 'getDestinationSectionValue'),
             (supply_organisation1, 'getSourceValue'),
             (supply_organisation1, 'getSourceSectionValue')))
    self.assertEqual(0, len(supply_movement.objectValues()))

    sequence.edit(
      produced_movement = produced_movement,
      operation_movement = operation_movement,
      component_movement = component_movement,
      supply_movement = supply_movement,
      produced_delivery_movement = related_simulation_movement.objectValues()[0].objectValues()[0],
    )

  def stepCreateProductionOrganisation2(self, sequence=None,
                                        sequence_list=None, **kw):
    """
      Create a organisation for supply
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                title='production_organisation2', **kw)

  def stepCreateSupplyOrganisation2(self, sequence=None, sequence_list=None,
                                        **kw):
    """
      Create a organisation for supply
    """
    self.stepCreateOrganisation(sequence=sequence, sequence_list=sequence_list,
                                title='supply_organisation2', **kw)

  def stepCreateTwoPhasesSC(self, sequence=None, sequence_list=None,
                             **kw):
    """
      Create a empty organisation
    """
    # Create supply chain
    self.stepCreateSourcingSC(sequence=sequence, sequence_list=sequence_list,
                              **kw)
    supply_chain = sequence.get('supply_chain')
    supply_chain.edit(
      title = 'Supply Chain Two Phases',
    )
    # Create production node
    production_organisation2  = sequence.get('production_organisation2')
    production_node2 = supply_chain.newContent(
                         portal_type=self.supply_node_portal_type)
    production_node2.edit(
      destination_value=production_organisation2
    )
    sequence.edit(production_node2=production_node2)
    # Create production link
    production_link2 = supply_chain.newContent(
                         portal_type=self.supply_link_portal_type)
    production_link2.edit(
      destination_value=production_node2,
      min_delay=5,
      max_delay=6,
      deliverable=0,
      industrial_phase_list=["phase2"]
    )
    # Link production_node2 and production_node1
    supply_link = supply_chain.newContent(
                         portal_type=self.supply_link_portal_type)
    production_node1 = sequence.get('production_node1')
    supply_link.edit(
      source_value=production_node2,
      destination_value=production_node1,
      min_delay=5,
      max_delay=6,
      deliverable=0,
      industrial_phase_list=[]
    )
    # Create supply node
    supply_organisation2  = sequence.get('supply_organisation2')
    supply_node2 = supply_chain.newContent(
                         portal_type=self.supply_node_portal_type)
    supply_node2.edit(
      destination_value=supply_organisation2
    )
    # Create sourcing link
    supply_link2 = supply_chain.newContent(
                         portal_type=self.supply_link_portal_type)
    supply_link2.edit(
      source_value=supply_node2,
      destination_value=production_node2,
      min_delay=5,
      max_delay=6,
      deliverable=0,
      industrial_phase_list=["supply_phase2"]
    )

  def stepCheckTwoPhasesSimulation(self, sequence=None, sequence_list=None,
                                   **kw):
    """
      Hardcoded check
    """
#     self.stepCheckSourcingSimulation(sequence=sequence,
#                                      sequence_list=sequence_list, **kw)
    self.stepCheckOrderSimulation(sequence=sequence,
                                  sequence_list=sequence_list, **kw)
    # Test simulation movement generated related to order line
    simulation_movement_list = sequence.get('simulation_movement_list')
    self.assertEqual(1, len(simulation_movement_list))
    order_line = sequence.get('order_line')
    related_simulation_movement_list = order_line.getDeliveryRelatedValueList()
    self.assertEqual(1, len(related_simulation_movement_list))
    related_simulation_movement = related_simulation_movement_list[0]
    self.assertEqual(related_simulation_movement,
                      simulation_movement_list[0])
    production_organisation1 = sequence.get('production_organisation1')
    # XXX FIXME test date
    self.checkObjectAttributes(
           related_simulation_movement, (
             (order_line.getQuantity(), 'getQuantity'),
             (order_line.getResourceValue(), 'getResourceValue'),
             (order_line.getVariationCategoryList(),
              'getVariationCategoryList'),
             (order_line.getDestinationValue(), 'getDestinationValue'),
             (order_line.getDestinationSectionValue(),
              'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    # Test next applied rule
    applied_rule_list = related_simulation_movement.objectValues()
    self.assertEqual(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_delivering_rule', \
                      applied_rule.getSpecialiseReference())
    # Test next applied rule
    simulation_movement_list = applied_rule.objectValues()
    self.assertEqual(1, len(simulation_movement_list))
    simulation_movement = simulation_movement_list[0]
    applied_rule_list = simulation_movement.objectValues()
    self.assertEqual(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_rule', \
                      applied_rule.getSpecialiseReference())
    # Test deeper simulation
    simulation_movement_list = list(applied_rule.objectValues())
    # FIXME
    self.assertEqual(4, len(simulation_movement_list))
    # Test produced resource
    produced_movement = applied_rule.pr
    resource = sequence.get('resource')
    production_organisation1 = sequence.get('production_organisation1')
    self.checkObjectAttributes(
           produced_movement, (
             (5, 'getQuantity'),
             (resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (production_organisation1, 'getDestinationValue'),
             (production_organisation1, 'getDestinationSectionValue'),
             (None, 'getSourceValue'),
             (None, 'getSourceSectionValue')))
    self.assertEqual(0, len(produced_movement.objectValues()))

    # Get modified resource (test later)
    modified_movement = applied_rule.mr_1
    simulation_movement_list.remove(produced_movement)
    simulation_movement_list.remove(modified_movement)
    # All code before is a stupid copy (except movement count)
    # Test consumed movement
    operation_resource = resource.portal_categories.resolveCategory(
                                              'operation/operation1')
    component_resource = sequence.get('component1')
#     for consumed_movement in (applied_rule.cr_1, applied_rule.cr_2):
    operation_movement = component_movement = None
    for consumed_movement in simulation_movement_list:
      if consumed_movement.getResourceValue() == operation_resource:
        operation_movement = consumed_movement
      else:
        component_movement = consumed_movement
    # Check operation movement
    self.checkObjectAttributes(
           operation_movement, (
             (10, 'getQuantity'),
             (operation_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    self.assertEqual(0, len(operation_movement.objectValues()))
    # Check component movement
    self.checkObjectAttributes(
           component_movement, (
             (30, 'getQuantity'),
             (component_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue')))
    self.assertEqual(1, len(component_movement.objectValues()))
    # Test supply applied rule
    applied_rule = component_movement.objectValues()[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_sourcing_rule', \
                      applied_rule.getSpecialiseReference())
    # Test supply movement
    simulation_movement_list = applied_rule.objectValues()
    # FIXME
    self.assertEqual(1, len(simulation_movement_list))
    # Test supply resource
    supply_movement = applied_rule.ts
    supply_organisation1 = sequence.get('supply_organisation1')
    self.checkObjectAttributes(
           supply_movement, (
             (30, 'getQuantity'),
             (component_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (production_organisation1, 'getDestinationValue'),
             (production_organisation1, 'getDestinationSectionValue'),
             (supply_organisation1, 'getSourceValue'),
             (supply_organisation1, 'getSourceSectionValue')))
    self.assertEqual(0, len(supply_movement.objectValues()))

    # Test modified movement
    resource = sequence.get('resource')
    production_organisation1 = sequence.get('production_organisation1')
    self.checkObjectAttributes(
           modified_movement, (
             (5, 'getQuantity'),
             (resource, 'getResourceValue'),
             (['industrial_phase/phase2'], 'getVariationCategoryList'),
             (production_organisation1, 'getSourceValue'),
             (production_organisation1, 'getSourceSectionValue'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue')))
    self.assertEqual(1, len(modified_movement.objectValues()))
    # Test next applied rule
    applied_rule_list = modified_movement.objectValues()
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_sourcing_rule', \
                      applied_rule.getSpecialiseReference())
    # Test deeper simulation
    simulation_movement_list = list(applied_rule.objectValues())
    self.assertEqual(1, len(simulation_movement_list))
    # Test produced resource
    sourcing_movement = simulation_movement_list[0]
    resource = sequence.get('resource')
    production_organisation1 = sequence.get('production_organisation1')
    production_organisation2 = sequence.get('production_organisation2')
    self.checkObjectAttributes(
           sourcing_movement, (
             (5, 'getQuantity'),
             (resource, 'getResourceValue'),
             (['industrial_phase/phase2'], 'getVariationCategoryList'),
             (production_organisation1, 'getDestinationValue'),
# XXX             (production_organisation1, 'getDestinationSectionValue'),
             (production_organisation2, 'getSourceValue'),
# XXX             (production_organisation2, 'getSourceSectionValue')))
           ))
    self.assertEqual(1, len(sourcing_movement.objectValues()))
    # Test next applied rule
    applied_rule_list = sourcing_movement.objectValues()
    self.assertEqual(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_rule', \
                      applied_rule.getSpecialiseReference())
    # Test deeper simulation
    simulation_movement_list = list(applied_rule.objectValues())
    # FIXME
    self.assertEqual(3, len(simulation_movement_list))
    # Test produced resource
    produced_movement = applied_rule.pr
    resource = sequence.get('resource')
    production_organisation2 = sequence.get('production_organisation2')
    self.checkObjectAttributes(
           produced_movement, (
             (5, 'getQuantity'),
             (resource, 'getResourceValue'),
             (['industrial_phase/phase2'], 'getVariationCategoryList'),
             (production_organisation2, 'getDestinationValue'),
# XXX             (production_organisation2, 'getDestinationSectionValue'),
             (None, 'getSourceValue'),
             (None, 'getSourceSectionValue')))
    self.assertEqual(0, len(produced_movement.objectValues()))

    simulation_movement_list.remove(produced_movement)
    # All code before is a stupid copy (except movement count)
    # Test consumed movement
    operation_resource = resource.portal_categories.resolveCategory(
                                              'operation/operation2')
    component_resource = sequence.get('component2')
    operation_movement = component_movement = None
    for consumed_movement in simulation_movement_list:
      if consumed_movement.getResourceValue() == operation_resource:
        operation_movement = consumed_movement
      else:
        component_movement = consumed_movement
    # Check operation movement
    self.checkObjectAttributes(
           operation_movement, (
             (15, 'getQuantity'),
             (operation_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation2, 'getSourceValue'),
# XXX              (production_organisation2, 'getSourceSectionValue')))
           ))
    self.assertEqual(0, len(operation_movement.objectValues()))
    # Check component movement
    self.checkObjectAttributes(
           component_movement, (
             (35, 'getQuantity'),
             (component_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (None, 'getDestinationValue'),
             (None, 'getDestinationSectionValue'),
             (production_organisation2, 'getSourceValue'),
# XXX              (production_organisation2, 'getSourceSectionValue')))
           ))
    self.assertEqual(1, len(component_movement.objectValues()))
    # Test supply applied rule
    applied_rule = component_movement.objectValues()[0]
    self.assertEqual("Applied Rule", applied_rule.getPortalType())
    self.assertEqual('default_transformation_sourcing_rule', \
                      applied_rule.getSpecialiseReference())
    # Test supply movement
    simulation_movement_list = applied_rule.objectValues()
    # FIXME
    self.assertEqual(1, len(simulation_movement_list))
    # Test supply resource
    supply_movement = applied_rule.ts
    supply_organisation2  = sequence.get('supply_organisation2')
    self.checkObjectAttributes(
           supply_movement, (
             (35, 'getQuantity'),
             (component_resource, 'getResourceValue'),
             ([], 'getVariationCategoryList'),
             (production_organisation2, 'getDestinationValue'),
# XXX              (production_organisation2, 'getDestinationSectionValue'),
             (supply_organisation2, 'getSourceValue'),
# XXX              (supply_organisation2, 'getSourceSectionValue')))
           ))
    self.assertEqual(0, len(supply_movement.objectValues()))

  SOURCING_ORDER_SEQUENCE = '\
                      CreateProductionOrganisation1 \
                      CreateSupplyOrganisation1 \
                      CreateSourcingSC \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateTransformation \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckSourcingSimulation \
                      ConfirmOrder \
                      Tic \
                      CheckSourcingSimulation \
                      '

class TestProductionOrder(TestProductionOrderMixin, ERP5TypeTestCase):
  """
    Test business template erp5_mrp
  """
  run_all_test = 1

  def getTitle(self):
    return "Production Order"

  @newSimulationExpectedFailure
  def test_01_testProductionSimulationExpand(self, quiet=0, run=run_all_test):
    """
      Test generation and update of order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateProductionSC \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateTransformation \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckProductionSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_02_testSourcingSimulationExpand(self, quiet=0,
                                                     run=run_all_test):
    """
      Test generation and update of order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateSupplyOrganisation1 \
                      CreateSourcingSC \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateTransformation \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckSourcingSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_03_testIndustrialPhase(self, quiet=0, run=run_all_test):
    """
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateProductionOrganisation2 \
                      CreateSupplyOrganisation1 \
                      CreateSupplyOrganisation2 \
                      CreateTwoPhasesSC \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateComponent2 \
                      CreateTransformation \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckTwoPhasesSimulation \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_04_testProductionSimulationBuild(self, quiet=0, run=run_all_test):
    """
    Test delivery building.
    XXX Test method still required
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateProductionSC \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateTransformation \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      Tic \
                      OrderOrder \
                      Tic \
                      ConfirmOrder \
                      Tic \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_05_testSourcingSimulationBuild(self, quiet=0,
                                          run=run_all_test):
    """
    Test delivery building.
    XXX Test method still required
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_list.addSequenceString(self.SOURCING_ORDER_SEQUENCE)
    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_06_testIndustrialPhase(self, quiet=0, run=run_all_test):
    """
    Test delivery building.
    XXX Test method still required
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is
    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateProductionOrganisation2 \
                      CreateSupplyOrganisation1 \
                      CreateSupplyOrganisation2 \
                      CreateTwoPhasesSC \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateComponent2 \
                      CreateTransformation \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      Tic \
                      OrderOrder \
                      Tic \
                      ConfirmOrder \
                      Tic \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def stepCopyPasteSupplyChain(self, sequence=None, sequence_list=None,
                               **kw):
    """
    Copy/Paste the supply chain
    """
    portal = self.getPortal()
    supply_chain_module = portal.getDefaultModule( \
                                   portal_type=self.supply_chain_portal_type)
    supply_chain = sequence.get('supply_chain')

    cb_data = supply_chain_module.manage_copyObjects([supply_chain.getId()])
    copied, = supply_chain_module.manage_pasteObjects(cb_data)
    pasted_sc = supply_chain_module[copied['new_id']]
    sequence.edit(pasted_sc=pasted_sc)

  def stepCheckPastedSupplyChain(self, sequence=None, sequence_list=None,
                                 **kw):
    """
    Check pasted supply chain
    """
    pasted_sc = sequence.get('pasted_sc')
    pasted_supply_node = pasted_sc.contentValues(portal_type='Supply Node')[0]
    pasted_supply_link = pasted_sc.contentValues(portal_type='Supply Link')[0]
    self.assertEqual(pasted_supply_node.getRelativeUrl(),
                      pasted_supply_link.getDestination())

  def test_07_testTransformationInteractionProductionOrderLine(self, quiet=0, run=run_all_test):
    """
    Test for setting/resetting Transformation on Production Order Line
    """
    if not run: return

    bootstrap_sequence_string = '\
                      CreateNotVariatedResource \
                      CreateOrder \
                      '
    sequence_list = SequenceList()

    # normal case
    sequence_string = bootstrap_sequence_string + '\
                      CreateTransformation \
                      Tic \
                      CreateOrderLineWithoutTransformation \
                      Tic \
                      CheckOrderLineTransformationIsSet \
                      '
    sequence_list.addSequenceString(sequence_string)

    # no transformation
    sequence_string = bootstrap_sequence_string + '\
                      CreateOrderLineWithoutTransformation \
                      Tic \
                      CheckOrderLineTransformationIsNotSet \
                      '
    sequence_list.addSequenceString(sequence_string)

    # transformation set, then not modified
    sequence_string = bootstrap_sequence_string + '\
                      CreateTransformation \
                      Tic \
                      CreateOrderLineWithoutTransformation \
                      Tic \
                      CheckOrderLineTransformationIsSet \
                      RemoveResourceFromOrderLine \
                      Tic \
                      CheckOrderLineTransformationIsNotSet \
                      '
    sequence_list.addSequenceString(sequence_string)

    # more than one transformation
    sequence_string = bootstrap_sequence_string + '\
                      CreateTransformation \
                      CreateTransformation \
                      Tic \
                      CreateOrderLineWithoutTransformation \
                      Tic \
                      CheckOrderLineTransformationIsNotSet \
                      '
    sequence_list.addSequenceString(sequence_string)

    # case of invalidated Transformation
    sequence_string = bootstrap_sequence_string + '\
                      CreateTransformation \
                      Tic \
                      ValidateTransformation \
                      InvalidateTransformation \
                      Tic \
                      CreateOrderLineWithoutTransformation \
                      Tic \
                      CheckOrderLineTransformationIsNotSet \
                      '
    sequence_list.addSequenceString(sequence_string)

    # case of invalidated Transformation and other
    sequence_string = bootstrap_sequence_string + '\
                      CreateTransformation \
                      Tic \
                      ValidateTransformation \
                      InvalidateTransformation \
                      Tic \
                      CreateTransformation \
                      Tic \
                      CreateOrderLineWithoutTransformation \
                      Tic \
                      CheckOrderLineTransformationIsSet \
                      '
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_08_testTransformationWithEfficiency(self, quiet=0, run=run_all_test):
    """
    Test, that efficiency from transformation applies correctly
    """
    if not run: return

    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateSupplyOrganisation1 \
                      CreateSourcingSC \
                      Tic \
                      CreateNotVariatedResource \
                      CreateComponent1 \
                      CreateEmptyTransformation \
                      FillTransformationWithResource \
                      Tic \
                      CreateTransformationTransformedResource \
                      FillTransformationTransformedResourceWithComponent1 \
                      SetTransformationTransformedResourceQuantity \
                      SetTransformationTransformedResourceEfficiency \
                      SetTransformationTransformedResourceIndustrialPhaseList \
                      Tic \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      SetOrderLineQuantity \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckEfficiencySimulation \
                      '
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)

    # case - we need Q:10.0, efficiency is 80% (we need more), producing 1.0
    self.transformation_transformed_resource_quantity = 10.0
    self.transformation_transformed_resource_efficiency = 0.8 # 80%
    self.transformation_transformed_resource_industrial_phase_list = ['supply_phase1',]

    self.production_order_line_quantity = 1.0
    self.quantity_after_efficiency_calculation = 12.5 # (1.0 * 10.0) / 0.8

    sequence_list.play(self)

    # case - we need Q:10.0, efficiency is None (normal, nothing set), producing 1.0
    self.transformation_transformed_resource_quantity = 10.0
    self.transformation_transformed_resource_efficiency = None
    self.transformation_transformed_resource_industrial_phase_list = ['supply_phase1',]

    self.production_order_line_quantity = 1.0
    self.quantity_after_efficiency_calculation = 10.0 # (1.0 * 10.0) / 1.0

    sequence_list.play(self)

    # case - we need Q:10.0, efficiency is 100% (normal), producing 1.0
    self.transformation_transformed_resource_quantity = 10.0
    self.transformation_transformed_resource_efficiency = 1.0
    self.transformation_transformed_resource_industrial_phase_list = ['supply_phase1',]

    self.production_order_line_quantity = 1.0
    self.quantity_after_efficiency_calculation = 10.0 # (1.0 * 10.0) / 1.0

    sequence_list.play(self)

    # case - we need Q:10.0, efficiency is 125% (miracle?), producing 1.0
    self.transformation_transformed_resource_quantity = 10.0
    self.transformation_transformed_resource_efficiency = 1.25
    self.transformation_transformed_resource_industrial_phase_list = ['supply_phase1',]

    self.production_order_line_quantity = 1.0
    self.quantity_after_efficiency_calculation = 8.0 # (1.0 * 10.0) / 1.25

    sequence_list.play(self)

    # case - we need Q:10.0, efficiency is -80% (nonsense?), producing 1.0
    self.transformation_transformed_resource_quantity = 10.0
    self.transformation_transformed_resource_efficiency = -0.8
    self.transformation_transformed_resource_industrial_phase_list = ['supply_phase1',]

    self.production_order_line_quantity = 1.0
    self.quantity_after_efficiency_calculation = -12.5 # (1.0 * 10.0) / -0.8

    sequence_list.play(self)

  @newSimulationExpectedFailure
  def test_09_testTransformationWithVariation(self, quiet=0, run=run_all_test):
    """
    Test, that variation from transformation works correctly on order

    Note: Read below variables to know, what and how was defined
    """
    if not run: return

    self.transformation_transformed_resource_quantity = 0.0
    self.transformation_transformed_resource_industrial_phase_list = ['supply_phase1',]
    self.production_order_line_quantity = 0.0
    self.variation_category_list = ['colour','size']

    self.colour_size_quantity_dict = {
      'green' : {
        'Man' : 1.0,
        'Woman' : 2.0
      },
      'blue' : {
        'Man' : 3.0,
        'Woman' : 4.0
      },
    }

    self.colour_size_variation_dict = {
      'green' : {
        'Man' : ('colour/green','size/Man'),
        'Woman' : ('colour/green','size/Woman')
      },
      'blue' : {
        'Man' : ('colour/blue','size/Man'),
        'Woman' : ('colour/blue','size/Woman')
      },
    }

    self.order_line_variation_category_list = [
      'size/Man',
      'size/Woman',
      'colour/green',
      'colour/blue',
    ]

    self.order_line_colour_size_quantity_dict = {
      'green' : {
        'Man' : 9.0,
        'Woman' : 8.0
      },
      'blue' : {
        'Man' : 7.0,
        'Woman' : 6.0
      },
    }

    sequence_string = '\
                      CreateProductionOrganisation1 \
                      CreateSupplyOrganisation1 \
                      CreateSourcingSC \
                      Tic \
                      CreateColourSizeVariatedResource \
                      CreateColourSizeVariatedComponent1 \
                      Tic \
                      CreateEmptyTransformation \
                      FillTransformationWithResource \
                      SetTransformationVariation \
                      Tic \
                      CreateTransformationTransformedResource \
                      FillTransformationTransformedResourceWithComponent1 \
                      SetTransformationTransformedResourceVariation \
                      SetTransformationTransformedResourceIndustrialPhaseList \
                      Tic \
                      SetTransformationTransformedResourceQuantityMatrix \
                      SetTransformationTransformedResourceVariationMatrix \
                      Tic \
                      CreateOrganisation \
                      CreateOrder \
                      CreateOrderLine \
                      SetOrderLineVariationCategories \
                      SetOrderLineQuantityMatrix \
                      Tic \
                      OrderOrder \
                      Tic \
                      CheckVariationSimulation \
                      ConfirmOrder \
                      Tic \
                      '
    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)

    sequence_list.play(self)

  def stepCreateEmptySC(self, sequence=None, sequence_list=None, **kw):
    """
      Create a empty Supply Chain
    """
    portal = self.getPortal()
    supply_chain_module = portal.getDefaultModule( \
                                   portal_type=self.supply_chain_portal_type)
    supply_chain = supply_chain_module.newContent( \
                                   portal_type=self.supply_chain_portal_type)
    supply_chain.edit(
      title = "Supply Chain Empty",
    )
    sequence.edit(empty_supply_chain=supply_chain)

  def stepCutPasteSupplyNodeInAnotherContainer(self, sequence=None,
                                               sequence_list=None, **kw):
    """
    Cut/Paste a supply node in another container
    """
    supply_chain = sequence.get('supply_chain')
    empty_supply_chain = sequence.get('empty_supply_chain')

    supply_node = supply_chain.contentValues(portal_type='Supply Node')[0]
    cb_data = supply_chain.manage_cutObjects([supply_node.getId()])
    self.assertEqual(len(empty_supply_chain.manage_pasteObjects(cb_data)), 1)

  def stepCheckPastedSupplyNode(self, sequence=None, sequence_list=None,
                                 **kw):
    """
    Check pasted supply node
    """
    supply_chain = sequence.get('supply_chain')
    empty_supply_chain = sequence.get('empty_supply_chain')

    supply_node = empty_supply_chain.contentValues(portal_type='Supply Node')[0]
    supply_link = supply_chain.contentValues(portal_type='Supply Link')[0]
    self.assertEqual(supply_node.getRelativeUrl(),
                      supply_link.getDestination())

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestProductionOrder))
  return suite
