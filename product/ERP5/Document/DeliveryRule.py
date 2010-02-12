##############################################################################
#
# Copyright (c) 2002 - 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from Products.ERP5Type import Permissions
from Products.ERP5.Document.Rule import Rule
from zLOG import LOG, WARNING

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
    if self._isBPM():
      Rule.expand(self, applied_rule,
          delivery_movement_type_list=delivery_movement_type_list, **kw)
      return
    existing_movement_list = []
    immutable_movement_list = []
    delivery = applied_rule.getDefaultCausalityValue()
    if delivery_movement_type_list is None:
      delivery_movement_type_list = self.getPortalDeliveryMovementTypeList()
    if delivery is not None:
      delivery_movement_list = delivery.getMovementList(
                                            portal_type=delivery_movement_type_list)
      # Check existing movements
      for movement in applied_rule.contentValues(portal_type=self.movement_type):
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
        sim_mvt = self._getDeliveryRelatedSimulationMovement(deliv_mvt)
        if sim_mvt is None:
          # create a new deliv_mvt
          if deliv_mvt.getParentUid() == deliv_mvt.getExplanationUid():
            # We are on a line
            new_id = deliv_mvt.getId()
          else:
            # We are on a cell
            new_id = "%s_%s" % (deliv_mvt.getParentId(), deliv_mvt.getId())
          # Generate the simulation deliv_mvt
          property_dict = self._getExpandablePropertyDict(
            applied_rule, deliv_mvt)
          new_sim_mvt = applied_rule.newContent(
              portal_type=self.movement_type,
              id=new_id,
              order_value=deliv_mvt,
              order_ratio=1,
              delivery_value=deliv_mvt,
              delivery_ratio=1,
              **property_dict)
        elif sim_mvt in existing_movement_list:
          if sim_mvt not in immutable_movement_list:
            # modification allowed
            property_dict = self._getExpandablePropertyDict(
              applied_rule, deliv_mvt)
            sim_mvt.edit(
                delivery_value=deliv_mvt,
                delivery_ratio=1,
                **property_dict)
          else:
            # modification disallowed, must compensate
            pass

      # Now we can set the last expand simulation state to the current state
      applied_rule.setLastExpandSimulationState(delivery.getSimulationState())
    # Pass to base class
    Rule.expand(self, applied_rule, **kw)

  def _getDeliveryRelatedSimulationMovement(self, delivery_movement):
    """Helper method to get the delivery related simulation movement.
    This method is more robust than simply calling getDeliveryRelatedValue
    which will not work if simulation movements are not indexed.
    """
    simulation_movement = delivery_movement.getDeliveryRelatedValue()
    if simulation_movement is not None:
      return simulation_movement
    # simulation movement was not found, maybe simply because it's not indexed
    # yet. We'll look in the simulation tree and try to find it anyway before
    # creating another simulation movement.
    # Try to find the one from trade model rule, which is the most common case
    # where we may expand again before indexation of simulation movements is
    # finished.
    delivery = delivery_movement.getExplanationValue()
    for movement in delivery.getMovementList():
      related_simulation_movement = movement.getDeliveryRelatedValue()
      if related_simulation_movement is not None:
        for applied_rule in related_simulation_movement.contentValues():
          for simulation_movement in applied_rule.contentValues():
            if simulation_movement.getDeliveryValue() == delivery_movement:
              return simulation_movement
    return None

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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getExpandablePropertyList')
  def getExpandablePropertyList(self, default=None):
    """
    Return a list of properties used in expand.
    """
    property_list = self._baseGetExpandablePropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(property_list) == 0:
      LOG("Order Rule , _getExpandablePropertyDict", WARNING,
                 "Hardcoded properties set, please define your rule correctly")
      property_list = (
        'aggregate_list',
        'base_application_list',
        'base_contribution_list',
        'description',
        'destination',
        'destination_account',
        'destination_function',
        'destination_section',
        'price',
        'price_currency',
        'quantity',
        'quantity_unit',
        'resource',
        'source',
        'source_account',
        'source_function',
        'source_section',
        'start_date',
        'stop_date',
        'variation_category_list',
        'variation_property_dict',
      )
    return property_list

  def _getInputMovementList(self, applied_rule):
    """Return list of movements from delivery"""
    delivery = applied_rule.getDefaultCausalityValue()
    movement_list = []
    if delivery is not None:
      existing_movement_list = applied_rule.objectValues()
      for movement in delivery.getMovementList(
        portal_type=delivery.getPortalDeliveryMovementTypeList()):
        simulation_movement = self._getDeliveryRelatedSimulationMovement(
          movement)
        if simulation_movement is None or \
               simulation_movement in existing_movement_list:
          movement_list.append(movement)
    return movement_list

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_path, current_property_dict):
    """Delivery specific update dict"""
    return {
      'order_list': [movement.getRelativeUrl()],
      'delivery_list': [movement.getRelativeUrl()],
    }
