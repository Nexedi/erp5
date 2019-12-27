
#############################################################################
#
# Copyright (c) 2008,2009 Nexedi SA and Contributors. All Rights Reserved.
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

r"""
Quantity Sign Movement Group is used to separate movements based on
the signs of the quantities.

This is probably used only in erp5_immobilisation. But this implementation
has a serious problem that the quantity sign is not set in a movement,
if the movement is created manually, because only this movement group
set that property with a builder. So a builder always creates new movements,
even if simulation movements match existing movements.

This is not easy to fix, because nobody available knows how this is supposed
to work precisely. In addition, it is questionable even that this movement
group makes sense. From accounting point of view, if the same account is
used, there is no problem in merging debits and credits.

So somebody must consult the spec of immobilisation accounting, and the
implementation of erp5_immobilisation seriously, to understand why and
whether this is really required.
"""

from erp5.component.document.MovementGroup import MovementGroup

class QuantitySignMovementGroup(MovementGroup):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.
  """
  meta_type = 'ERP5 Quantity Sign Movement Group'
  portal_type = 'Quantity Sign Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    quantity = movement.getQuantity()
    property_dict['quantity_sign'] = cmp(quantity, 0)
    return property_dict

  def _separate(self, movement_list, **kw):
    if not movement_list:
      return []

    tmp_list = [[], [], []] # -1:minus, 0:zero, 1:plus
    for movement in movement_list:
      tmp_list[cmp(movement.getQuantity(), 0)].append(movement)
    if len(tmp_list[1]):
      if len(tmp_list[-1]):
        return[
          [tmp_list[1]+tmp_list[0], {'quantity_sign':1}],
          [tmp_list[-1], {'quantity_sign':-1}],
          ]
      else:
        return[
          [tmp_list[1]+tmp_list[0], {'quantity_sign':1}],
          ]
    elif len(tmp_list[-1]):
      return[
        [tmp_list[-1]+tmp_list[0], {'quantity_sign':-1}],
        ]
    else:
      return [
        [tmp_list[0], {'quantity_sign':0}],
        ]

  def test(self, document, property_dict, **kw):
    if document.getQuantitySign() == property_dict['quantity_sign']:
      return True, property_dict
    else:
      return False, property_dict
