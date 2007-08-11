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

from CopyToTarget import CopyToTarget

class ResourceBackpropagation(CopyToTarget):
  """
  This solver is based on CopyToTarget, but it also backpropagates resource
  related properties and categories
  """
  def _generateValueDeltaDict(self, simulation_movement):
    """
    Get interesting values
    XXX: better description is possible. But is it needed ?
    """
    # Get interesting value
    old_quantity = simulation_movement.getQuantity()
    old_start_date = simulation_movement.getStartDate()
    old_stop_date = simulation_movement.getStopDate()
    new_quantity = simulation_movement.getDeliveryQuantity() * \
                   simulation_movement.getDeliveryRatio()
    new_start_date = simulation_movement.getDeliveryStartDateList()[0]
    new_stop_date = simulation_movement.getDeliveryStopDateList()[0]
    # Calculate delta
    quantity_ratio = 0
    if old_quantity not in (None,0.0): # XXX: What if quantity happens to be an integer ?
      quantity_ratio = new_quantity / old_quantity
    start_date = None
    stop_date = None
    if new_start_date is not None and old_start_date is not None:
      start_date = new_start_date
    if new_stop_date is not None and old_stop_date is not None:
      stop_date = new_stop_date
    return {
      'quantity_ratio': quantity_ratio,
      'start_date': start_date,
      'stop_date': stop_date,
      'resource_list' :
          simulation_movement.getDeliveryValue().getResourceList(),
      'variation_category_list':
          simulation_movement.getDeliveryValue().getVariationCategoryList(),
      'variation_property_dict':
          simulation_movement.getDeliveryValue().getVariationPropertyDict(),
    }

  def _generateValueDict(self, simulation_movement, quantity_ratio=1, 
                         start_date=None, stop_date=None,
                         resource_list=[],
                         variation_category_list=[],
                         variation_property_dict={},
                         **value_delta_dict):
    """
    Generate values to save on simulation movement.
    """
    value_dict = {}
    # Modify quantity, start_date, stop_date
    if start_date is not None:
      value_dict['start_date'] = start_date
    if stop_date is not None:
      value_dict['stop_date'] = stop_date
    value_dict['quantity'] = simulation_movement.getQuantity() * quantity_ratio
    if resource_list:
      value_dict['resource_list'] = resource_list
    if variation_category_list:
      value_dict['variation_category_list'] = variation_category_list
    if variation_property_dict:
      value_dict['variation_property_dict'] = variation_property_dict

    return value_dict
