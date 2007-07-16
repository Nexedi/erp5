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
from Products.ERP5.Document.DeliveryRule import DeliveryRule
from zLOG import LOG, WARNING

class OrderRule(DeliveryRule):
  """
  Order Rule object make sure an Order in the similation
  is consistent with the real order

  WARNING: what to do with movement split ?
  """
  # CMF Type Definition
  meta_type = 'ERP5 Order Rule'
  portal_type = 'Order Rule'

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
    
    movement_type = 'Simulation Movement'
    existing_movement_list = []
    immutable_movement_list = []
    order = applied_rule.getDefaultCausalityValue()
    if order is not None:
      order_movement_list = order.getMovementList()
      # check existing movements
      for movement in applied_rule.contentValues(portal_type=movement_type):
        if (not movement.getLastExpandSimulationState() in
            order.getPortalReservedInventoryStateList() and
            not movement.getLastExpandSimulationState() in
            order.getPortalCurrentInventoryStateList()) and \
            not self._isTreeDelivered([movement]):

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
        property_dict = self._getExpandablePropertyDict(applied_rule, movement)      
        if related_order is None:
          if movement.getParentUid() == movement.getExplanationUid():
            # We are on a line
            new_id = movement.getId()
          else:
            # We are on a cell
            new_id = "%s_%s" % (movement.getParentId(), movement.getId())
          # Generate a simulation movement
          applied_rule.newContent(
              portal_type=movement_type,
              id=new_id,
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
                                 default_property_list=None, **kw):
    """
    Return a Dictionary with the Properties used to edit 
    the simulation movement
    """
    property_dict = {}

    if default_property_list is None:
      # XXX Hardcoded value
#       LOG("Order Rule , _getPropertiesTo", WARNING,
#                                 "Hardcoded properties set")
      default_property_list = (
        'source',
        'source_section', 
        'destination', 
        'destination_section', 
        'start_date', 
        'stop_date',
        'resource', 
        'variation_category_list',
        'variation_property_dict', 
        'aggregate_list', 
        'price', 
        'price_currency',
        'quantity', 
        'quantity_unit', 
      )
  
      for prop in default_property_list:
         property_dict[prop] = movement.getProperty(prop)
       
    return property_dict
