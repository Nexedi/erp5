##############################################################################
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from erp5.component.document.CausalityAssignmentMovementGroup \
      import CausalityAssignmentMovementGroup

class DeliveryCausalityAssignmentMovementGroup(CausalityAssignmentMovementGroup):
  """Like CausalityAssignmentMovementGroup, but using the delivery relation of
  simulation movements instead of order relation. This is intended to be used
  in deeper level of simulation tree.
  """
  meta_type = 'ERP5 Delivery Causality Assignment Movement Group'
  portal_type = 'Delivery Causality Assignment Movement Group'

  def _addCausalityToEdit(self, movement, property_dict=None):
    if property_dict is None:
      property_dict = {}
    if movement.getParentValue().isRootAppliedRule():
      # Here movement probably comes from invoice rule, in that situation, we
      # are not able to go up and find a delivery.
      return property_dict

    parent = movement.getParentValue().getParentValue()
    # Go upper into the simulation tree in order to find a delivery link
    while parent.getDeliveryValue() is None and not(parent.isRootAppliedRule()):
      parent = parent.getParentValue()
    delivery_movement = parent.getDeliveryValue()
    if delivery_movement is not None:
      delivery = delivery_movement.getExplanationValue()
      causality = property_dict.get('causality_list', [])
      delivery_url = delivery.getRelativeUrl()
      if delivery_url not in causality:
        causality.append(delivery_url)
        property_dict['causality_list'] = causality
    return property_dict

