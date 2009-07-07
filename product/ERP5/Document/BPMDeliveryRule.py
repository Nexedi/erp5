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

class BPMDeliveryRule(BPMRule):
  """
    DISCLAIMER: Refer to BPMRule docstring disclaimer.

    This is BPM enabled Delivery Rule.
  """

  # CMF Type Definition
  meta_type = 'ERP5 BPM Delivery Rule'
  portal_type = 'BPM Delivery Rule'

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
    existing_movement_list = []
    immutable_movement_list = []
    delivery = applied_rule.getDefaultCausalityValue()
    if delivery_movement_type_list is None:
      delivery_movement_type_list = self.getPortalDeliveryMovementTypeList()
    if delivery is not None:
      delivery_movement_list = delivery.getMovementList(
                                 portal_type=delivery_movement_type_list)
      # Check existing movements
      for movement in applied_rule.contentValues(
          portal_type=self.movement_type):
        if not movement.isFrozen():
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
          property_dict = self.self._getExpandablePropertyDict(applied_rule,
              deliv_mvt)
          new_sim_mvt = applied_rule.newContent(
              portal_type=self.movement_type,
              id=new_id,
              order_value=deliv_mvt,
              order_ratio=1,
              delivery_value=deliv_mvt,
              delivery_ratio=1,
              deliverable=1,

              **property_dict
          )
        elif sim_mvt in existing_movement_list:
          if sim_mvt not in immutable_movement_list:
            # modification allowed
            # XXX Hardcoded value
            sim_mvt.edit(
                delivery_value=deliv_mvt,
                delivery_ratio=1,
                deliverable=1,
                force_update=1,
                **property_dict
                )
          else:
            # modification disallowed, must compensate
            raise NotImplementedError('BPM *have* to support')

      # Now we can set the last expand simulation state to the current state
      applied_rule.setLastExpandSimulationState(delivery.getSimulationState())
    # Pass to base class
    BPMRule.expand(self, applied_rule, **kw)

  security.declareProtected(Permissions.AccessContentsInformation, 'isStable')
  def isStable(self, applied_rule):
    """
    Checks that the applied_rule is stable
    """
    return 0

  # Deliverability / orderability
  def isOrderable(self, movement):
    return 1

  def isDeliverable(self, movement):
    if movement.getSimulationState() in movement \
        .getPortalDraftOrderStateList():
      return 0
    return 1

