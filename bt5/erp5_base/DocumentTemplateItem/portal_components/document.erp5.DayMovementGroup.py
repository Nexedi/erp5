
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
from Products.ERP5Type.DateUtils import addToDate
from DateTime import DateTime

class DayMovementGroup(MovementGroup):
  """
  This movement group is used to group movements which belong to the same day
  """
  meta_type = 'ERP5 Day Movement Group'
  portal_type = 'Day Movement Group'

  def _getPropertyDict(self, movement, **kw):
    property_dict = {}
    start_date = self._getStartDate(movement)
    property_dict['start_date'] = start_date
    property_dict['stop_date'] = addToDate(start_date, day=1)
    return property_dict

  def test(self, document, property_dict, **kw):
    start_date = property_dict['start_date']
    stop_date = property_dict['stop_date']
    if document.getStartDate() <= start_date < stop_date <= document.getStopDate():
      return True, property_dict
    else:
      return False, property_dict

  def _getStartDate(self, movement):
    start_date = DateTime(movement.getStartDate() is not None and\
                          movement.getStartDate().Date() or None)
    return start_date
