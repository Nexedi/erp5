
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

class TitleMovementGroup(MovementGroup):
  """
  This movement group is used to group movements that have the same
  title.
  """
  meta_type = 'ERP5 Title Movement Group'
  portal_type = 'Title Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    property_dict['title'] = self._getTitle(movement)
    return property_dict

  def test(self, document, property_dict, **kw):
    # If title is different, we want to update existing document instead
    # of creating a new one.
    return True, property_dict

  def _getTitle(self, movement):
    title = None
    if 'Cell' in movement.getPortalType():
      movement = movement.getParentValue()
    if movement.hasTitle():
      title = movement.getTitle()
    return title
