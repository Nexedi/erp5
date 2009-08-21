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
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Rule import Rule
from Products.ERP5.Document.DeliveryRule import DeliveryRule
from zLOG import LOG, WARNING

class OrderRule(DeliveryRule):
  """
  Order Rule object make sure an Order in the simulation
  is consistent with the real order

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Order Rule'
  portal_type = 'Order Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Simulation workflow
  security.declareProtected(Permissions.ModifyPortalContent, 'expand')
  def expand(self, applied_rule, force=0, **kw):
    """
      Expands the Order to a new simulation tree.
      expand is only allowed to modify a simulation movement if it doesn't
      have a delivery relation yet.

      If the movement is in ordered or planned state, has no delivered
      child, and is not in order, it can be deleted.
      Else, if the movement is in ordered or planned state, has no
      delivered child, and is in order, it can be modified.
      Else, it cannot be modified.
    """
    if self._isBPM():
      DeliveryRule.expand(self, applied_rule, force=force, **kw)
      return

    movement_type = 'Simulation Movement'
    existing_movement_list = []
    immutable_movement_list = []
    order = applied_rule.getDefaultCausalityValue()
    if order is not None:
      order_movement_list = order.getMovementList(
                     portal_type=order.getPortalOrderMovementTypeList())
      # check existing movements
      for movement in applied_rule.contentValues(portal_type=movement_type):
        if (not movement.getLastExpandSimulationState() in
            order.getPortalReservedInventoryStateList() and
            not movement.getLastExpandSimulationState() in
            order.getPortalCurrentInventoryStateList()) and \
            not movement._isTreeDelivered():

          movement_order = movement.getOrderValue()
          if movement_order in order_movement_list:
            existing_movement_list.append(movement)
          else:
            applied_rule._delObject(movement.getId())
        else:
          existing_movement_list.append(movement)
          immutable_movement_list.append(movement)
       
      # this dict simulates getOrderRelatedValue, but it will not work if an
      # order was generated from multiple applied rules
      order_movement_dict = {}
      for s_m in applied_rule.objectValues():
        order_movement = s_m.getOrderValue()
        if order_movement is not None:
          order_movement_dict[order_movement.getPath()] = s_m
      # Create or modify movements
      for movement in order_movement_list:
        related_order = order_movement_dict.get(movement.getPath(), None)
        if related_order is None:
          related_order = movement.getOrderRelatedValue()
        property_dict = self._getExpandablePropertyDict(
                                            applied_rule, movement)
        if related_order is None:
          # Generate a simulation movement
          # Do not try to create meaningfull IDs, as order movement can be
          # hierarchicals
          applied_rule.newContent(
              portal_type=movement_type,
              order_value=movement,
              order_ratio=1,
              delivery_ratio=1,
              deliverable=1,
              **property_dict )
          
        elif related_order in existing_movement_list:
          if related_order not in immutable_movement_list:
            # modification allowed
            related_order.edit(
              order_value=movement,
                **property_dict)
            
            #related_order.setLastExpandSimulationState(order.getSimulationState())
            
          else:
            # modification disallowed, must compensate
            pass

          # Now we can set the last expand simulation state to the current state
          applied_rule.setLastExpandSimulationState(order.getSimulationState())
    # Pass to base class
    Rule.expand(self, applied_rule, force=force, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isStable')
  def isStable(self, applied_rule):
    """
    Checks that the applied_rule is stable
    """
    LOG('OrderRule.isStable', WARNING, 'Not Implemented')
    return 1

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isDivergent')
  def isDivergent(self, movement):
    """
    Checks that the movement is divergent
    """
    return Rule.isDivergent(self, movement)

  security.declareProtected(Permissions.AccessContentsInformation,
                            '_getExpandablePropertyDict')
  def _getExpandablePropertyDict(self, applied_rule, movement,
      business_path=None, **kw):
    """
    Return a Dictionary with the Properties used to edit 
    the simulation movement
    """
    if self._isBPM():
      return DeliveryRule._getExpandablePropertyDict(self, applied_rule,
          movement, business_path, **kw)
    property_dict = {}

    default_property_list = self.getExpandablePropertyList()
    # For backward compatibility, we keep for some time the list
    # of hardcoded properties. Theses properties should now be
    # defined on the rule itself
    if len(default_property_list) == 0:
      LOG("Order Rule , _getExpandablePropertyDict", WARNING,
                 "Hardcoded properties set, please define your rule correctly")
      default_property_list = (
        'source',
        'source_section',
        'source_function',
        'source_account',
        'destination',
        'destination_section',
        'destination_function',
        'destination_account',
        'start_date',
        'stop_date',
        'description',
        'resource',
        'variation_category_list',
        'variation_property_dict',
        'base_contribution_list',
        'aggregate_list',
        'price',
        'price_currency',
        'quantity',
        'quantity_unit',
      )
  
    for prop in default_property_list:
       property_dict[prop] = movement.getProperty(prop)
       
    return property_dict

  def _getInputMovementList(self, applied_rule):
    """Input movement list comes from order"""
    order = applied_rule.getDefaultCausalityValue()
    if order is not None:
      return order.getMovementList(
                     portal_type=order.getPortalOrderMovementTypeList())
    return []

  def _getExpandablePropertyUpdateDict(self, applied_rule, movement,
      business_path, current_property_dict):
    """Order rule specific update dictionary"""
    return {
      'order_list': [movement.getRelativeUrl()],
      'deliverable': 1,
    }
