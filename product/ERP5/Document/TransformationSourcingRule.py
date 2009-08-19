##############################################################################
#
# Copyright (c) 2002, 2005 Nexedi SARL and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import ExtensionClass

import zope.interface
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName

from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class ProductionOrderError(Exception): pass
class TransformationSourcingRuleError(Exception): pass

class TransformationSourcingRuleMixin(ExtensionClass.Base):
  """
    Mixin class used by TransformationSourcingRule and TransformationRule
  """
  # Declarative security
  security = ClassSecurityInfo()

  security.declareProtected(Permissions.View,
                            'getSupplyChain')
  def getSupplyChain(self, applied_rule):
    """
      Get the SupplyChain.
    """
    # Get the SupplyChain to use
    supply_chain_portal_type = "Supply Chain"
    order = applied_rule.getRootAppliedRule().getCausalityValue()
    supply_chain = order.getSpecialiseValue(
                               portal_type=supply_chain_portal_type)
    if supply_chain is None:
      raise ProductionOrderError,\
            "No SupplyChain defined on %s" % str(order)
    else:
      return supply_chain

  def getCurrentSupplyLink(self, movement):
    """
      Get the current SupplyLink
    """
    # Get the current supply link
    supply_link_portal_type = "Supply Link"
    current_supply_link = movement.getCausalityValue(
                                  portal_type=supply_link_portal_type)
    return current_supply_link

  security.declareProtected(Permissions.ModifyPortalContent, 
                            '_buildMovementList')
  def _buildMovementList(self, applied_rule, movement_dict,activate_kw=None,**kw):
    """
      For each movement in the dictionnary, test if the movement already
      exists.
      If not, create it.
      Then, update the movement attributes.
    """
    for movement_id in movement_dict.keys():
      movement = applied_rule.get(movement_id)
      # Create the movement if it does not exist
      if movement is None:
        movement = applied_rule.newContent(
                        portal_type=self.simulation_movement_portal_type,
                        id=movement_id,
                        activate_kw=activate_kw
        )
      # We shouldn't modify frozen movements
      elif movement.isFrozen():
        # FIXME: this is not perfect, instead of just skipping this one, we
        # should generate a compensation movement
        continue
      # Update movement properties
      movement.edit(activate_kw=activate_kw, **(movement_dict[movement_id]))

  security.declareProtected(Permissions.View, 'getTransformation')
  def getTransformation(self, movement):
    """
    Get transformation related to used by the applied rule.
    """
    production_order_movement = movement.getRootSimulationMovement().\
                                                   getOrderValue()
    # XXX Acquisition can be use instead
    parent_uid = production_order_movement.getParentUid()
    explanation_uid = production_order_movement.getExplanationUid()
    if parent_uid == explanation_uid:
      production_order_line = production_order_movement
    else:
      production_order_line = production_order_movement.getParentValue()
    script = production_order_line._getTypeBasedMethod('_getTransformation') 
    if script is not None:
      transformation = script()
    else:
      line_transformation = production_order_line.objectValues(
                portal_type=self.getPortalTransformationTypeList())
      if len(line_transformation)==1:
        transformation = line_transformation[0]
      else:
        transformation = production_order_line.getSpecialiseValue(
                           portal_type=self.getPortalTransformationTypeList())
    return transformation

class TransformationSourcingRule(TransformationSourcingRuleMixin, Rule):
    """
      Transformation Sourcing Rule object make sure
      items required in a Transformation are sourced
    """
    # CMF Type Definition
    meta_type = 'ERP5 Transformation Sourcing Rule'
    portal_type = 'Transformation Sourcing Rule'
    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)
    zope.interface.implements(interfaces.IPredicate,
                              interfaces.IRule )

    # Class variable 
    simulation_movement_portal_type = "Simulation Movement"

    security.declareProtected(Permissions.ModifyPortalContent, 'expand')
    def expand(self, applied_rule, activate_kw=None,**kw):
      """
        Expands the current movement downward.
        -> new status -> expanded
        An applied rule can be expanded only if its parent movement
        is expanded.
      """
      parent_movement = applied_rule.getParentValue()
      # Calculate the previous supply link
      supply_chain = self.getSupplyChain(parent_movement.getParentValue())
      parent_supply_link = self.getCurrentSupplyLink(parent_movement)
      previous_supply_link_list = supply_chain.\
                     getPreviousPackingListSupplyLinkList(
                                                    parent_supply_link,
                                                    movement=parent_movement)
      if len(previous_supply_link_list) == 0:
        raise TransformationSourcingRuleError,\
              "Expand must not be called on %r" %\
                  applied_rule.getRelativeUrl()
      else:
        movement_dict = {}
        for previous_supply_link in previous_supply_link_list:
          # Calculate the source
          source_value = None
          source_node = previous_supply_link.getSourceValue()
          if source_node is not None:
            source_value = source_node.getDestinationValue()
          source_section_value = previous_supply_link.getSourceSectionValue()
          # Generate the dict
          stop_date = parent_movement.getStartDate()
          movement_dict.update({
            "ts": {
              'source_value': source_value,
              'source_section_value': source_section_value,
              'destination_value': parent_movement.getSourceValue(),
              'destination_section_value': \
                  parent_movement.getSourceSectionValue(),
              'resource_value': parent_movement.getResourceValue(),
              'variation_category_list': parent_movement.\
                                            getVariationCategoryList(),
              "variation_property_dict": \
                            parent_movement.getVariationPropertyDict(),
              'quantity': parent_movement.getNetQuantity(), # getNetQuantity to support efficency from transformation
              'price': parent_movement.getPrice(),
              'quantity_unit': parent_movement.getQuantityUnit(),
              'start_date': previous_supply_link.calculateStartDate(stop_date),
              'stop_date': stop_date,
              'deliverable': 1,
              # Save the value of the current supply link
              'causality_value': previous_supply_link,
            }
          })
        # Build the movement
        self._buildMovementList(applied_rule, movement_dict,
                                activate_kw=activate_kw)
      # Create one submovement which sources the transformation
      Rule.expand(self, applied_rule, activate_kw=activate_kw, **kw)

    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self, applied_rule, solution_list):
      """
        Solve inconsistency according to a certain number of solutions
        templates. This updates the

        -> new status -> solved

        This applies a solution to an applied rule. Once
        the solution is applied, the parent movement is checked.
        If it does not diverge, the rule is reexpanded. If not,
        diverge is called on the parent movement.
      """

    security.declareProtected(Permissions.ModifyPortalContent, 'diverge')
    def diverge(self, applied_rule):
      """
        -> new status -> diverged

        This basically sets the rule to "diverged"
        and blocks expansion process
      """

#    # Solvers
#    security.declareProtected(Permissions.View, 'isDivergent')
#    def isDivergent(self, applied_rule):
#      """
#        Returns 1 if divergent rule
#      """
#
#    security.declareProtected(Permissions.View, 'getDivergenceList')
#    def getDivergenceList(self, applied_rule):
#      """
#        Returns a list Divergence descriptors
#      """
#
#    security.declareProtected(Permissions.View, 'getSolverList')
#    def getSolverList(self, applied_rule):
#      """
#        Returns a list Divergence solvers
#      """

    def isDeliverable(self, m):
      resource = m.getResource()
      if m.getResource() is None:
        return 0
      if resource.find('operation/') >= 0:
        return 0
      else:
        return 1

    def isOrderable(self, m):
      return 0

