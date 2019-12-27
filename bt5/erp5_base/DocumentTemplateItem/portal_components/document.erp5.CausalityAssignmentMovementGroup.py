
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

from erp5.component.document.MovementGroup import MovementGroup

class CausalityAssignmentMovementGroup(MovementGroup):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.

  This movement group is used in order to define the causality on lines
  and cells.
  """
  meta_type = 'ERP5 Causality Assignment Movement Group'
  portal_type = 'Causality Assignment Movement Group'

  def _getPropertyDict(self, movement, **kw):
    return self._addCausalityToEdit(movement)

  def _separate(self, movement_list, **kw):
    if not movement_list:
      return []
    property_dict = {}
    for movement in movement_list:
      self._addCausalityToEdit(movement, property_dict)
    return [[movement_list, property_dict]]

  def test(self, movement, property_dict, **kw):
    # We can always update.
    return True, property_dict

  def _addCausalityToEdit(self, movement, property_dict=None):
    if property_dict is None:
      property_dict = {}
    causality_list = property_dict.get('causality_list', [])
    root_movement = movement.getRootSimulationMovement()
    # 'order' category is deprecated. it is kept for compatibility.
    movement_list = root_movement.getOrderList() or \
                    root_movement.getDeliveryList()
    for delivery_movement in movement_list:
      if delivery_movement not in causality_list:
        causality_list.append(delivery_movement)
    property_dict['causality_list'] = causality_list
    return property_dict
