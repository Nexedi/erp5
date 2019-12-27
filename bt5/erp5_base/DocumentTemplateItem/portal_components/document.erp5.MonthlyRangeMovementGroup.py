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
# Foundation, Inc., 51 Franklin Street - Fifth Floor, Boston, MA
# 02110-1301, USA.
#
##############################################################################

from erp5.component.document.MovementGroup import MovementGroup
from Products.ERP5Type.DateUtils import atTheEndOfPeriod


class MonthlyRangeMovementGroup(MovementGroup):
  """
  The purpose of MovementGroup is to define how movements are grouped,
  and how values are updated from simulation movements.

  This movement group is used to collect movements that have datetime
  which is in the same month.
  """
  meta_type = 'ERP5 Monthly Range Movement Group'
  portal_type = 'Monthly Range Movement Group'

  def _getPropertyDict(self, movement, **kw):
    """Gather start_date and stop_date, converge them to the end of month.
    """
    property_dict = {}
    for property_name in self.getTestedPropertyList() or ('start_date', 'stop_date'):
      date = movement.getProperty(property_name, None)
      if date is not None:
        end_of_month = atTheEndOfPeriod(date, 'month')-1
        property_dict[property_name] = end_of_month
    return property_dict

  def test(self, document, property_dict, property_list=None, **kw):
    for property_name in self.getTestedPropertyList() or ('start_date', 'stop_date'):
      date = property_dict.get(property_name, None)
      if date is None:
        return False, property_dict
      target_date = document.getProperty(property_name, None)
      if target_date is None:
        return False, property_dict
      if date.year() != target_date.year() or \
        date.month() != target_date.month():
        return False, property_dict
    return True, property_dict
