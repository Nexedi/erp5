# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
#                    Romain Courteaud <romain@nexedi.com>
#                    Łukasz Nowak <luke@nexedi.com>
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
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.BPMRule import BPMRule
from Products.ERP5.Document.BPMDeliveryRule import BPMDeliveryRule
from zLOG import LOG, WARNING

class BPMOrderRule(BPMDeliveryRule):
  """
    DISCLAIMER: Refer to BPMRule docstring disclaimer.

    This is BPM enabled Order Rule.
  """
  # CMF Type Definition
  meta_type = 'ERP5 BPM Order Rule'
  portal_type = 'BPM Order Rule'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.AppliedRule
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

    existing_movement_list = []
    immutable_movement_list = []
    order = applied_rule.getDefaultCausalityValue()
    business_process = applied_rule.getBusinessProcessValue()
    if order is not None:
      order_movement_list = order.getMovementList(
                     portal_type=order.getPortalOrderMovementTypeList())
      # check existing movements
      for simulation_movement in applied_rule.contentValues(
          portal_type=self.movement_type):
        if not simulation_movement.isFrozen():
          movement_order = simulation_movement.getOrderValue()
          if movement_order in order_movement_list:
            existing_movement_list.append(simulation_movement)
          else:
            applied_rule._delObject(simulation_movement.getId())
        else:
          existing_movement_list.append(simulation_movement)
          immutable_movement_list.append(simulation_movement)

      # this dict simulates getOrderRelatedValue, but it will not work if an
      # order was generated from multiple applied rules
      order_movement_dict = {}
      for s_m in applied_rule.objectValues():
        order_movement = s_m.getOrderValue()
        if order_movement is not None:
          order_movement_dict[order_movement.getPath()] = s_m

      # Create or modify movements
      for order_movement in order_movement_list:
        related_order = order_movement_dict.get(order_movement.getPath(),
            None)
        if related_order is None:
          related_order = order_movement.getOrderRelatedValue()

        movement_and_path_list = []
        for business_path in business_process.getPathValueList(
                            self.getProperty('trade_phase_list'),
                            order_movement):
          movement_and_path_list.append((order_movement, business_path))

        if len(movement_and_path_list) > 1:
          raise NotImplementedError

        for movement, business_path in movement_and_path_list:
          property_dict = self._getExpandablePropertyDict(
                                         applied_rule, movement,
                                         business_path)
          property_dict.update(order_value=order_movement)
        if related_order is None:
          # Generate a simulation movement
          # Do not try to create meaningfull IDs, as order movement can be
          # hierarchical
          applied_rule.newContent(
              portal_type=self.movement_type,
              order_ratio=1,
              delivery_ratio=1,
              deliverable=1,
              **property_dict)
        elif related_order in existing_movement_list:
          if related_order not in immutable_movement_list:
            # modification allowed
            related_order.edit(
                **property_dict)
          else:
            # modification disallowed, must compensate
            raise NotImplementedError('BPM *have* to support compensation')

          # Now we can set the last expand simulation state to the current
          # state
          applied_rule.setLastExpandSimulationState(
              order.getSimulationState())
    # Pass to base class
    BPMRule.expand(self, applied_rule, force=force, **kw)

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
    return BPMRule.isDivergent(self, movement)
