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
                    , PropertySheet.Task
                    )

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, delivery_movement_type_list=None, **kw):
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
    if delivery_movement_type_list is None:
      delivery_movement_type_list = self.getPortalDeliveryMovementTypeList()
    if delivery is not None:
      delivery_movement_list = delivery.getMovementList(
                                            portal_type=delivery_movement_type_list)
      # Check existing movements
      for movement in applied_rule.contentValues(portal_type=movement_type):
        if movement.getLastExpandSimulationState() not in \
          self.getPortalCurrentInventoryStateList():
          # XXX: This condition is quick and dirty hack - knowing if Simulation
          #      Movement is frozen shall not be ever hardcoded, this is BPM
          #      configuration
          movement_delivery = movement.getDeliveryValue()
          if not movement._isTreeDelivered(ignore_first=1) and \
              movement_delivery not in delivery_movement_list:
            applied_rule._delObject(movement.getId())
          else:
            existing_movement_list.append(movement)
        else:
          existing_movement_list.append(movement)
          immutable_movement_list.append(movement)

      # Create or modify movements
      for deliv_mvt in delivery_movement_list:
        sim_mvt = deliv_mvt.getDeliveryRelatedValue()
        if sim_mvt is None:
          # create a new deliv_mvt
          if deliv_mvt.getParentUid() == deliv_mvt.getExplanationUid():
            # We are on a line
            new_id = deliv_mvt.getId()
          else:
            # We are on a cell
            new_id = "%s_%s" % (deliv_mvt.getParentId(), deliv_mvt.getId())
          # Generate the simulation deliv_mvt
          # XXX Hardcoded value
          new_sim_mvt = applied_rule.newContent(
              portal_type=movement_type,
              id=new_id,
              order_value=deliv_mvt,
              order_ratio=1,
              delivery_value=deliv_mvt,
              delivery_ratio=1,
              deliverable=1,

              source=deliv_mvt.getSource(),
              source_section=deliv_mvt.getSourceSection(),
              source_function=deliv_mvt.getSourceFunction(),
              source_account=deliv_mvt.getSourceAccount(),
              destination=deliv_mvt.getDestination(),
              destination_section=deliv_mvt.getDestinationSection(),
              destination_function=deliv_mvt.getDestinationFunction(),
              destination_account=deliv_mvt.getDestinationAccount(),
              start_date=deliv_mvt.getStartDate(),
              stop_date=deliv_mvt.getStopDate(),

              resource=deliv_mvt.getResource(),
              variation_category_list=deliv_mvt.getVariationCategoryList(),
              variation_property_dict=deliv_mvt.getVariationPropertyDict(),
              aggregate_list=deliv_mvt.getAggregateList(),

              quantity=deliv_mvt.getQuantity(),
              quantity_unit=deliv_mvt.getQuantityUnit(),
              price=deliv_mvt.getPrice(),
              price_currency=deliv_mvt.getPriceCurrency(),
              base_contribution_list=deliv_mvt.getBaseContributionList(),
              base_application_list=deliv_mvt.getBaseApplicationList(),
          )
        elif sim_mvt in existing_movement_list:
          if sim_mvt not in immutable_movement_list:
            # modification allowed
            # XXX Hardcoded value
            sim_mvt.edit(
                delivery_value=deliv_mvt,
                delivery_ratio=1,
                deliverable=1,

                source=deliv_mvt.getSource(),
                source_section=deliv_mvt.getSourceSection(),
                source_function=deliv_mvt.getSourceFunction(),
                source_account=deliv_mvt.getSourceAccount(),
                destination=deliv_mvt.getDestination(),
                destination_section=deliv_mvt.getDestinationSection(),
                destination_function=deliv_mvt.getDestinationFunction(),
                destination_account=deliv_mvt.getDestinationAccount(),
                start_date=deliv_mvt.getStartDate(),
                stop_date=deliv_mvt.getStopDate(),

                resource=deliv_mvt.getResource(),
                variation_category_list=deliv_mvt.getVariationCategoryList(),
                variation_property_dict=deliv_mvt.getVariationPropertyDict(),
                aggregate_list=deliv_mvt.getAggregateList(),

                quantity=deliv_mvt.getQuantity(),
                quantity_unit=deliv_mvt.getQuantityUnit(),
                price=deliv_mvt.getPrice(),
                price_currency=deliv_mvt.getPriceCurrency(),
                base_contribution_list=deliv_mvt.getBaseContributionList(),
                base_application_list=deliv_mvt.getBaseApplicationList(),
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
  def isStable(self, applied_rule):
    """
    Checks that the applied_rule is stable
    """
    return 0

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

