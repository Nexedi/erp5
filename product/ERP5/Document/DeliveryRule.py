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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.Rule import Rule

from zLOG import LOG

class DeliveryRule(Rule):
  """
    Delivery Rule object make sure orphaned movements in a Delivery
    (ie. movements which have no explanation in terms of order)
    are part of the simulation process
  """

  # CMF Type Definition
  meta_type = 'ERP5 Delivery Rule'
  portal_type = 'Delivery Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  __implements__ = ( Interface.Predicate,
                     Interface.Rule )

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    )

  def _test(self, movement):
    """
    Default behaviour of DeliveryRule.test
    Tests if the rule (still) applies
    """
    # A delivery rule never applies 
    # since it is always explicitely instanciated
    return 0

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, **kw):
    """
    Expands the additional Delivery movements to a new simulation tree.
    Expand is only allowed to create or modify simulation movements for
    delivery lines which are not already linked to another simulation
    movement.

    If the movement is not in current state, has no delivered child, and not
    in delivery movements, it can be deleted.
    Else if the movement is not in current state, it can be modified.
    Else, it cannot be modified.
    """
    movement_type = 'Simulation Movement'
    existing_movement_list = []
    immutable_movement_list = []
    delivery = applied_rule.getDefaultCausalityValue()
    if delivery is not None:
      delivery_movement_list = delivery.getMovementList()
      # Check existing movements
      for movement in applied_rule.contentValues(portal_type=movement_type):
        if movement.getLastExpandSimulationState() not in \
            delivery.getPortalCurrentInventoryStateList():

          movement_delivery = movement.getDeliveryValue()
          if not self._isTreeDelivered([movement], ignore_first=1) and \
              movement_delivery not in delivery_movement_list:
            applied_rule._delObject(movement.getId())
          else:
            existing_movement_list.append(movement)
        else:
          existing_movement_list.append(movement)
          immutable_movement_list.append(movement)

      # Create or modify movements
      for movement in delivery.getMovementList():
        related_delivery = movement.getDeliveryRelatedValue()
        if related_delivery is None:
          # create a new movement
          if movement.getParentUid() == movement.getExplanationUid():
            # We are on a line
            new_id = movement.getId()
          else:
            # Weare on a cell
            new_id = "%s_%s" % (movement.getParentId(), movement.getId())
          # Generate the simulation movement
          new_sim_mvt = applied_rule.newContent(
              portal_type=movement_type,
              id=new_id,
              order_value=movement,
              order_ratio=1,
              delivery_value=movement,
              delivery_ratio=1,
              deliverable=1,
              source=movement.getSource(),
              source_section=movement.getSourceSection(),
              destination=movement.getDestination(),
              destination_section=movement.getDestinationSection(),
              quantity=movement.getQuantity(),
              resource=movement.getResource(),
              variation_category_list=movement.getVariationCategoryList(),
              variation_property_dict=movement.getVariationPropertyDict(),
              start_date=movement.getStartDate(),
              stop_date=movement.getStopDate())
        elif related_delivery in existing_movement_list:
          if related_delivery not in immutable_movement_list:
            # modification allowed
            related_delivery.edit(
                delivery_value=movement,
                delivery_ratio=1,
                deliverable=1,
                source=movement.getSource(),
                source_section=movement.getSourceSection(),
                destination=movement.getDestination(),
                destination_section=movement.getDestinationSection(),
                quantity=movement.getQuantity(),
                resource=movement.getResource(),
                variation_category_list=movement.getVariationCategoryList(),
                variation_property_dict=movement.getVariationPropertyDict(),
                start_date=movement.getStartDate(),
                stop_date=movement.getStopDate(),
                force_update=1)
          else:
            # modification disallowed, must compensate
            pass

      # Now we can set the last expand simulation state to the current state
      applied_rule.setLastExpandSimulationState(delivery.getSimulationState())
    # Pass to base class
    Rule.expand(self, applied_rule, **kw)

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

  # Solvers
  security.declareProtected(Permissions.AccessContentsInformation, 'isStable')
  def isStable(self, movement):
    """
    Checks that the applied_rule is stable
    """
    return 0

  security.declareProtected(Permissions.AccessContentsInformation, 'isDivergent')
  def isDivergent(self, movement):
    """
    Checks that the movement is divergent
    """
    return Rule.isDivergent(self, movement)

  security.declareProtected(Permissions.AccessContentsInformation, 'getDivergenceList')
  def getDivergenceList(self, applied_rule):
    """
      Returns a list Divergence descriptors
    """

  security.declareProtected(Permissions.AccessContentsInformation, 'getSolverList')
  def getSolverList(self, applied_rule):
    """
      Returns a list Divergence solvers
    """

  # Deliverability / orderability
  def isOrderable(self, movement):
    return 1

  def isDeliverable(self, movement):
    if movement.getSimulationState() in movement.getPortalDraftOrderStateList():
      return 0
    return 1

