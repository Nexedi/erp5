##############################################################################
#
# Copyright (c) 2002-2013 Nexedi SA and Contributors. All Rights Reserved.
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
##############################################################################

from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.ERP5.Document.PresencePeriod import PresencePeriod

class GroupCalendarAssignment(PresencePeriod):
  # CMF Type Definition
  meta_type = 'ERP5 Group Calendar Assignment'
  portal_type = 'Group Calendar Assignment'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected( Permissions.AccessContentsInformation,
                             'asMovementList')
  def asMovementList(self):
    """
    Generate multiple movement from a single one.
    It is used for cataloging a movement multiple time in
    the movement/stock tables.

    Ex: a movement have multiple destinations.
    asMovementList returns a list a movement context with different
    single destination.
    """
    result = []
    group_calendar = self.getSpecialiseValue()
    if None in (self.getDestinationUid(), group_calendar):
      return result
    presence_period_list = group_calendar.objectValues(portal_type="Group Presence Period")
    for presence_period in presence_period_list:
      for from_date, to_date in presence_period._getDatePeriodList():
        if from_date.greaterThanEqualTo(self.getStartDate()) and \
            to_date.lessThanEqualTo(self.getStopDate() or group_calendar.getStopDate()):
          result.append(self.asContext(self, start_date=to_date, stop_date=from_date))
    return result
