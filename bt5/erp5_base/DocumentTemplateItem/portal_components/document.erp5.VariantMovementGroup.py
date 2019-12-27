
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

class VariantMovementGroup(MovementGroup):
  """
  This movement group is used to group movements that have the same
  variation category list.
  """
  meta_type = 'ERP5 Variant Movement Group'
  portal_type = 'Variant Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    category_list = movement.getVariationCategoryList()
    if category_list is None:
      category_list = []
    category_list.sort()
    property_dict['variation_category_list'] = category_list
    return property_dict

  def test(self, document, property_dict, **kw):
    category_list = document.getVariationCategoryList()
    if category_list is None:
      category_list = []
    category_list.sort()
    if property_dict['variation_category_list'] == category_list:
      return True, property_dict
    else:
      return False, property_dict
