##############################################################################
#
# Copyright (c) 2010 Nexedi KK and Contributors. All Rights Reserved.
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

class PropertyGroupingMovementGroup(MovementGroup):
  """
  This movement group is used to group movements without assignment.
  It only take care that the movements are going to separate or not.
  """
  meta_type = 'ERP5 Property Grouping Movement Group'
  portal_type = 'Property Grouping Movement Group'

  def test(self, document, property_dict, **kw):
    # We did not assign the properties into the document thanks to this movement group.
    # Therefore their is no way to compare the properties between the document
    # and the movements. In other words, they are always different.
    # So, we only check the update_always flag on the movement group setting here.
    if self.isUpdateAlways():
      return True, {}
    return False, {}

  def _separate(self, movement_list, **kw):
    if not movement_list:
      return []

    movement_dict = {}
    tested_property_list = self.getTestedPropertyList()
    for movement in movement_list:
      key_value_list = []
      getProperty = movement.getProperty
      for prop in tested_property_list:
        key_value_list.append((prop, getProperty(prop)))
      # key_value_list as a grouping key
      movement_dict.setdefault(tuple(key_value_list), []).append(movement)
    return [(movement_list, {}) for movement_list in movement_dict.values()]
