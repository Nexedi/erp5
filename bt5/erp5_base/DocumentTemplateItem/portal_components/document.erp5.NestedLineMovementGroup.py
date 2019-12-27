##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
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

class NestedLineMovementGroup(MovementGroup):
  """
  This MovementGroup is only used to multiple lines control.
  No more effect.
  """

  meta_type = 'ERP5 Nested Line Movement Group'
  portal_type = 'Nested Line Movement Group'

  def _getPropertyDict(self, movement, **kw):
    return {}

  def test(self, document, property_dict, property_list=None, **kw):
    if property_list not in (None, []):
      target_property_list = [x for x in self.getTestedPropertyList() \
                              if x in property_list]
    else:
      target_property_list = self.getTestedPropertyList()
    for prop in target_property_list:
      if property_dict[prop] != document.getProperty(prop, None):
        return False, property_dict
    return True, property_dict

  def isBranch(self):
    return True
