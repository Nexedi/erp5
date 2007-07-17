##############################################################################
#
# Copyright (c) 2005 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
#          Romain Courteaud <romain@nexedi.com>
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

#
# Skeleton ZopeTestCase
#

from random import randint

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

# Needed in order to have a log file inside the current folder
os.environ['EVENT_LOG_FILE'] = os.path.join(os.getcwd(), 'zLOG.log')
os.environ['EVENT_LOG_SEVERITY'] = '-300'

from Testing import ZopeTestCase
from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from AccessControl.SecurityManagement import newSecurityManager, \
                                             noSecurityManager
from DateTime import DateTime
from Acquisition import aq_base, aq_inner
from zLOG import LOG
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.tests.Sequence import Sequence, SequenceList
import time
import os
from Products.ERP5Type import product_path
from Products.CMFCore.utils import getToolByName
from testOrder import TestOrderMixin

class TestProductionOrderMixin(TestOrderMixin):

  run_all_test = 1
  order_portal_type = 'Production Order'
  order_line_portal_type = 'Production Order Line'
  supply_chain_portal_type = 'Supply Chain'
  supply_node_portal_type = 'Supply Node'
  supply_link_portal_type = 'Supply Link'
  component_portal_type = 'Apparel Component'
  transformation_portal_type = 'Apparel Transformation'
  transformed_resource_portal_type = \
                        'Apparel Transformation Transformed Resource'
  operation_line_portal_type = 'Apparel Transformation Operation'
  order_workflow_id='production_order_workflow'

  def getBusinessTemplateList(self):
    """
    """
    return ('erp5_base','erp5_pdm', 'erp5_trade', 'erp5_apparel', 'erp5_mrp')

  def createCategories(self):
    """ 
      Light install create only base categories, so we create 
      some categories for testing them
    """
    TestOrderMixin.createCategories(self)
    operation_category_list = ['operation1', 'operation2']
    if len(self.category_tool.operation.contentValues()) == 0:
      for category_id in operation_category_list:
        o = self.category_tool.operation.newContent(
                                               portal_type='Category',
                                               id=category_id)

  def stepClearActivities(self, sequence=None, sequence_list=None, 
                          **kw):
    """
    Clear activity tables
    """
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

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
      title = "Supply Chain Test",
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
      Create a empty order
    """
    portal = self.getPortal()
    order_module = portal.getDefaultModule(portal_type=self.order_portal_type)
    order = order_module.newContent(portal_type=self.order_portal_type)
    organisation = sequence.get('organisation')
    supply_chain = sequence.get('supply_chain')
    order.edit(
      title = "Production Order",
      start_date = self.datetime + 10,
      stop_date = self.datetime + 20,
      destination_value=organisation,
      destination_section_value=organisation,
      specialise_value=supply_chain
    )
    sequence.edit(order=order)

  def stepCreateOrderLine(self, sequence=None, sequence_list=None, **kw):
    """
      Create a empty order line
    """
    order = sequence.get('order')
    order_line = order.newContent(portal_type=self.order_line_portal_type)
    resource = sequence.get('resource')
    transformation = sequence.get('transformation')
    order_line.edit(
      title="Order Line",
      resource_value=resource,
      specialise_value=transformation,
      quantity=5
    )
    sequence.edit(order_line=order_line)

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
      self.assertEquals(0, len(related_applied_rule_list))
    else:
      self.assertEquals(1, len(related_applied_rule_list))
      applied_rule = related_applied_rule_list[0].getObject()
      sequence.edit(applied_rule=applied_rule)
      self.failUnless(applied_rule is not None)
      self.failUnless(order_state, \
                      applied_rule.getLastExpandSimulationState())
      # Test if applied rule has a specialise value with default_order_rule
      portal_rules = getToolByName(order, 'portal_rules')
      # XXX hardcoded value
      self.assertEquals(portal_rules.default_production_order_rule, \
                        applied_rule.getSpecialiseValue())
      
      simulation_movement_list = applied_rule.objectValues()
      sequence.edit(simulation_movement_list=simulation_movement_list)

  def checkObjectAttributes(self, object, attribute_list):
    LOG('checkObjectAttributes object.getPath',0,object.getPath())
    for value, attribute in attribute_list:
      try:
        self.assertEquals(value,
                          getattr(object, attribute)())
      except AssertionError:
        LOG('Raise Assertion error',0,'')
        LOG('object.getQuantity()',0,object.getQuantity())
        LOG('object.__dict__',0,object.__dict__)
        LOG('object.getOrderValue().getQuantity()',0,object.getOrderValue().getQuantity())
        raise AssertionError, "Attribute: %s, Value: %s, Result: %s" %\
                    (attribute, value, getattr(object, attribute)())

  def stepCheckProductionSimulation(self, sequence=None, sequence_list=None,
                                    **kw):
    """
      Hardcoded check
    """
    self.stepCheckOrderSimulation(sequence=sequence,
                                  sequence_list=sequence_list, **kw)
    # Test simulation movement generated related to order line
    simulation_movement_list = sequence.get('simulation_movement_list')
    self.assertEquals(1, len(simulation_movement_list))
    order_line = sequence.get('order_line')
    related_simulation_movement_list = order_line.getOrderRelatedValueList()
    self.assertEquals(1, len(related_simulation_movement_list))
    related_simulation_movement = related_simulation_movement_list[0]
    self.assertEquals(related_simulation_movement,
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
    self.assertEquals(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_rule, \
                      applied_rule.getSpecialiseValue())
    # Test deeper simulation 
    simulation_movement_list = applied_rule.objectValues()
    self.assertEquals(2, len(simulation_movement_list))
    # Test consumed movement
    transformation = sequence.get('transformation')
    consumed_movement_id = 'cr_%s_1' % transformation.getId()
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
    self.assertEquals(1, len(simulation_movement_list))
    order_line = sequence.get('order_line')
    related_simulation_movement_list = order_line.getOrderRelatedValueList()
    self.assertEquals(1, len(related_simulation_movement_list))
    related_simulation_movement = related_simulation_movement_list[0]
    self.assertEquals(related_simulation_movement,
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
    self.assertEquals(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_rule, \
                      applied_rule.getSpecialiseValue())
    # Test deeper simulation 
    simulation_movement_list = list(applied_rule.objectValues())
    # FIXME
    self.assertEquals(3, len(simulation_movement_list))
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
    self.assertEquals(0, len(produced_movement.objectValues()))

    simulation_movement_list.remove(produced_movement)
    # All code before is a stupid copy (except movement count)
    # Test consumed movement
    operation_resource = resource.portal_categories.resolveCategory(
                                              'operation/operation1')
    component_resource = sequence.get('component1')
#     for consumed_movement in (applied_rule.cr_1, applied_rule.cr_2):
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
    self.assertEquals(0, len(operation_movement.objectValues()))
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
    self.assertEquals(1, len(component_movement.objectValues()))
    # Test supply applied rule
    applied_rule = component_movement.objectValues()[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_sourcing_rule, \
                      applied_rule.getSpecialiseValue())
    # Test supply movement
    simulation_movement_list = applied_rule.objectValues()
    # FIXME
    self.assertEquals(1, len(simulation_movement_list))
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
    self.assertEquals(0, len(supply_movement.objectValues()))

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
    self.assertEquals(1, len(simulation_movement_list))
    order_line = sequence.get('order_line')
    related_simulation_movement_list = order_line.getOrderRelatedValueList()
    self.assertEquals(1, len(related_simulation_movement_list))
    related_simulation_movement = related_simulation_movement_list[0]
    self.assertEquals(related_simulation_movement,
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
    self.assertEquals(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_rule, \
                      applied_rule.getSpecialiseValue())
    # Test deeper simulation 
    simulation_movement_list = list(applied_rule.objectValues())
    # FIXME
    self.assertEquals(4, len(simulation_movement_list))
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
    self.assertEquals(0, len(produced_movement.objectValues()))

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
    self.assertEquals(0, len(operation_movement.objectValues()))
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
    self.assertEquals(1, len(component_movement.objectValues()))
    # Test supply applied rule
    applied_rule = component_movement.objectValues()[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_sourcing_rule, \
                      applied_rule.getSpecialiseValue())
    # Test supply movement
    simulation_movement_list = applied_rule.objectValues()
    # FIXME
    self.assertEquals(1, len(simulation_movement_list))
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
    self.assertEquals(0, len(supply_movement.objectValues()))

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
    self.assertEquals(1, len(modified_movement.objectValues()))
    # Test next applied rule
    applied_rule_list = modified_movement.objectValues()
    applied_rule = applied_rule_list[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_sourcing_rule, \
                      applied_rule.getSpecialiseValue())
    # Test deeper simulation 
    simulation_movement_list = list(applied_rule.objectValues())
    self.assertEquals(1, len(simulation_movement_list))
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
    self.assertEquals(1, len(sourcing_movement.objectValues()))
    # Test next applied rule
    applied_rule_list = sourcing_movement.objectValues()
    self.assertEquals(1, len(applied_rule_list))
    applied_rule = applied_rule_list[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_rule, \
                      applied_rule.getSpecialiseValue())
    # Test deeper simulation 
    simulation_movement_list = list(applied_rule.objectValues())
    # FIXME
    self.assertEquals(3, len(simulation_movement_list))
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
    self.assertEquals(0, len(produced_movement.objectValues()))

    simulation_movement_list.remove(produced_movement)
    # All code before is a stupid copy (except movement count)
    # Test consumed movement
    operation_resource = resource.portal_categories.resolveCategory(
                                              'operation/operation2')
    component_resource = sequence.get('component2')
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
    self.assertEquals(0, len(operation_movement.objectValues()))
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
    self.assertEquals(1, len(component_movement.objectValues()))
    # Test supply applied rule
    applied_rule = component_movement.objectValues()[0]
    self.assertEquals("Applied Rule", applied_rule.getPortalType())
    portal_rules = getToolByName(applied_rule, 'portal_rules')
    self.assertEquals(portal_rules.default_transformation_sourcing_rule, \
                      applied_rule.getSpecialiseValue())
    # Test supply movement
    simulation_movement_list = applied_rule.objectValues()
    # FIXME
    self.assertEquals(1, len(simulation_movement_list))
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
    self.assertEquals(0, len(supply_movement.objectValues()))

    
class TestProductionOrder(TestProductionOrderMixin, ERP5TypeTestCase):
  """
    Test business template erp5_mrp
  """
  run_all_test = 1

  def getTitle(self):
    return "Production Order"

  def test_01_testProductionSimulationExpand(self, quiet=0, run=run_all_test):
    """
      Test generation and update of order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is 
    sequence_string = '\
                      ClearActivities \
                      CreateProductionOrganisation1 \
                      CreateProductionSC \
                      CreateVariatedResource \
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

  def test_02_testSourcingSimulationExpand(self, quiet=0, 
                                                     run=run_all_test):
    """
      Test generation and update of order applied rule.
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is 
    sequence_string = '\
                      ClearActivities \
                      CreateProductionOrganisation1 \
                      CreateSupplyOrganisation1 \
                      CreateSourcingSC \
                      CreateVariatedResource \
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

  def test_03_testIndustrialPhase(self, quiet=0, run=run_all_test):
    """
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is 
    sequence_string = '\
                      ClearActivities \
                      CreateProductionOrganisation1 \
                      CreateProductionOrganisation2 \
                      CreateSupplyOrganisation1 \
                      CreateSupplyOrganisation2 \
                      CreateTwoPhasesSC \
                      CreateVariatedResource \
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

  def test_04_testProductionSimulationBuild(self, quiet=0, run=run_all_test):
    """
    Test delivery building.
    XXX Test method still required
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is 
    sequence_string = '\
                      ClearActivities \
                      CreateProductionOrganisation1 \
                      CreateProductionSC \
                      CreateVariatedResource \
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

  def test_05_testSourcingSimulationBuild(self, quiet=0, 
                                          run=run_all_test):
    """
    Test delivery building.
    XXX Test method still required
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is 
    sequence_string = '\
                      ClearActivities \
                      CreateProductionOrganisation1 \
                      CreateSupplyOrganisation1 \
                      CreateSourcingSC \
                      CreateVariatedResource \
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

  def test_06_testIndustrialPhase(self, quiet=0, run=run_all_test):
    """
    Test delivery building.
    XXX Test method still required
    """
    if not run: return
    sequence_list = SequenceList()
    # Test when order is 
    sequence_string = '\
                      ClearActivities \
                      CreateProductionOrganisation1 \
                      CreateProductionOrganisation2 \
                      CreateSupplyOrganisation1 \
                      CreateSupplyOrganisation2 \
                      CreateTwoPhasesSC \
                      CreateVariatedResource \
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
    self.assertEquals(pasted_supply_node.getRelativeUrl(),
                      pasted_supply_link.getDestination())

  def test_50_testCopyPaste(self, quiet=0, run=run_all_test):
    """
    Check that relation are changed when doing a copy/paste,
    on supply chain
    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
            ClearActivities \
            CreateProductionOrganisation1 \
            CreateProductionSC \
            CopyPasteSupplyChain \
            Tic \
            CheckPastedSupplyChain \
                      '
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
    copied, = empty_supply_chain.manage_pasteObjects(cb_data)

  def stepCheckPastedSupplyNode(self, sequence=None, sequence_list=None, 
                                 **kw):
    """
    Check pasted supply node
    """
    supply_chain = sequence.get('supply_chain')
    empty_supply_chain = sequence.get('empty_supply_chain')

    supply_node = empty_supply_chain.contentValues(portal_type='Supply Node')[0]
    supply_link = supply_chain.contentValues(portal_type='Supply Link')[0]
    self.assertEquals(supply_node.getRelativeUrl(),
                      supply_link.getDestination())

  def test_51_testCutPasteInAnotherContainer(self, quiet=0, run=run_all_test):
    """
    Check that relations are changed when doing a copy/paste,
    on a supply chain.

    The point in this test is that internal relations should be updated
    when copying an object. Suppose that a document D1 contains sub-objects
    S1_1 and S1_2, and S1_1 is related to S1_2. When copying D1 to D2,
    S2_1 and S2_2 are also copied from S1_1 and S1_2. Now S2_1 should be
    related to S2_2, instead of S1_2.

    Good:

    D1 -+- S1_1          D1 -+- S1_1   D2 -+- S2_1
        |    |      =>       |    |        |    |
        |    v               |    v        |    v
        +- S1_2              +- S1_2       +- S2_2

    Bad:

    D1 -+- S1_1          D1 -+- S1_1   D2 -+- S2_1
        |    |      =>       |    |      __|_/    
        |    v               |    v     /  |     
        +- S1_2              +- S1_2<--/   +- S2_2

    """
    if not run: return
    sequence_list = SequenceList()
    sequence_string = '\
            ClearActivities \
            CreateProductionOrganisation1 \
            CreateProductionSC \
            CreateEmptySC \
            CutPasteSupplyNodeInAnotherContainer \
            Tic \
            CheckPastedSupplyNode \
                      '
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)
