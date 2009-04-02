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

from Products.ERP5.Document.MovementGroup import MovementGroup

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

  def _separate(self, movement_list):
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
    parent = movement
    # Go upper into the simulation tree in order to find an order link
    while parent.getOrderValue() is None and not(parent.isRootAppliedRule()):
      parent = parent.getParentValue()
    order_movement = parent.getOrderValue()
    if order_movement is not None:
      causality = property_dict.get('causality_list', [])
      order_movement_url = order_movement.getRelativeUrl()
      if order_movement_url not in causality:
        causality.append(order_movement_url)
        property_dict['causality_list'] = causality
    return property_dict
