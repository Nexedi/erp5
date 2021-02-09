from __future__ import absolute_import
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

from .CopyToTarget import CopyToTarget

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
    value_delta_dict = CopyToTarget._generateValueDeltaDict(
      self, simulation_movement)
    value_delta_dict.update(
      {
      'resource_list' :
          simulation_movement.getDeliveryValue().getResourceList(),
      'variation_category_list':
          simulation_movement.getDeliveryValue().getVariationCategoryList(),
      'variation_property_dict':
          simulation_movement.getDeliveryValue().getVariationPropertyDict(),
      })

    return value_delta_dict

  def _generateValueDict(self, simulation_movement, quantity_ratio=1,
                         start_date_delta=0, stop_date_delta=0,
                         resource_list=[],
                         variation_category_list=[],
                         variation_property_dict={},
                         **value_delta_dict):
    """
    Generate values to save on simulation movement.
    """
    value_dict = CopyToTarget._generateValueDict(
      self, simulation_movement, quantity_ratio=quantity_ratio,
      start_date_delta=start_date_delta, stop_date_delta=stop_date_delta,
      resource_list=resource_list,
      variation_category_list=variation_category_list,
      variation_property_dict=variation_property_dict, **value_delta_dict)
    # Modify resource etc.
    if resource_list:
      value_dict['resource_list'] = resource_list
    if variation_category_list:
      value_dict['variation_category_list'] = variation_category_list
    if variation_property_dict:
      value_dict['variation_property_dict'] = variation_property_dict

    return value_dict
