
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
from Products.ERP5Type import PropertySheet

class PropertyAssignmentMovementGroup(MovementGroup):
  """
  This movement group is used to set the value of a property on the delivery,
  line or cell based on the value of this property on the grouped simulation
  movements.
  The are multiple ways of grouping:
   - min of all property values of simulation movements
   - max of all property values of simulation movements
   - average of all property values of simulation movements
   - "comon": the property value, only if it's the same for all simulation
     movements, None otherwise.
  None values are always ignored, even in 'common' mode
  """
  meta_type = 'ERP5 Property Assignment Movement Group'
  portal_type = 'Property Assignment Movement Group'

  property_sheets = (
      PropertySheet.PropertyAssignmentMovementGroup, )

  def test(self, movement, property_dict, **kw):
    # We can always update.
    return True, property_dict

  def _separate(self, movement_list, **kw):
    if not movement_list:
      return []

    property_dict = {}

    for prop in self.getTestedPropertyList():
      grouping_method = self.getGroupingMethod()
      if not grouping_method:
        break

      property_list = [movement.getProperty(prop) for movement in
             movement_list if movement.getProperty(prop) is not None]

      if grouping_method == 'max':
        if len(property_list):
          property_dict[prop] = max(property_list)
      elif grouping_method == 'min':
        if len(property_list):
          property_dict[prop] = min(property_list)
      elif grouping_method == 'avg':
        if len(property_list) and self._can_calculate_average(property_list):
          property_dict[prop] = self._calculate_average(property_list)
      else:
        assert grouping_method == 'common'
        if len(set(property_list)) == 1:
          property_dict[prop] = property_list[0]
    return [[movement_list, property_dict]]

  def _can_calculate_average(self, property_list):
    """Test if we can calculate an average from this property list, only
    numeric types are supported.
    """
    for prop in property_list:
      try:
        float(prop)
      except (TypeError, ValueError):
        return False
    return True

  def _calculate_average(self, property_list):
    """Calculate the average property from the list, only numeric types are
    supported.
    """
    return sum(property_list) / len(property_list)

