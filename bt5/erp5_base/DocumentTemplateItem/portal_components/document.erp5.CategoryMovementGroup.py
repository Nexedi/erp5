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

from erp5.component.document.PropertyMovementGroup import PropertyMovementGroup

class CategoryMovementGroup(PropertyMovementGroup):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.

  This movement group is used to group movements that have the same
  categories (eg. source, destination, etc.).

  Like for equivalence tester, 'specialise' categories aren't sorted
  alphabetically because the original order is important (see for example
  CompositionMixin, and how Amount Generator Lines can override others).
  """
  meta_type = 'ERP5 Category Movement Group'
  portal_type = 'Category Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    getProperty = movement.getProperty
    for prop in self.getTestedPropertyList():
      list_prop = prop + '_list'
      property_dict[list_prop] = (list if prop == 'specialise' else
                                  sorted)(getProperty(list_prop) or ())
    return property_dict

  def test(self, document, property_dict, property_list=None, **kw):
    if self.isUpdateAlways():
      return True, property_dict
    if property_list not in (None, []):
      target_property_list = [x for x in self.getTestedPropertyList() \
                              if x in property_list]
    else:
      target_property_list = self.getTestedPropertyList()
    getProperty = document.getProperty
    for prop in target_property_list:
      list_prop = prop + '_list'
      if property_dict[list_prop] != (list if prop == 'specialise' else
                                      sorted)(getProperty(list_prop)):
        return False, property_dict
    return True, property_dict
