# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2006,2007 Nexedi SARL and Contributors. All Rights Reserved.
#                    Rafael Monnerat <rafael@nexedi.com>
#                    Courteaud Romain <romain@nexedi.com>
#
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

from copy import copy
from AccessControl import ClassSecurityInfo
from DateTime import DateTime

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.mixin.periodicity import PeriodicityMixin
from Products.ERP5.Document.Movement import Movement
from Products.ERP5Type.DateUtils import addToDate

class PresencePeriod(Movement, PeriodicityMixin):
  """
  Presence Period is used to add available time of the user in a
  period of Time
  """

  meta_type = 'ERP5 Presence Period'
  portal_type = 'Presence Period'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Amount
                    , PropertySheet.Task
                    , PropertySheet.Movement
                    , PropertySheet.Arrow
                    , PropertySheet.Periodicity
                    , PropertySheet.Path
                    , PropertySheet.SortIndex
                    )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isAccountable')
  def isAccountable(self):
    """
    For now, consider that it's always accountable
    """
    return 1

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getInventoriatedQuantity')
  def getInventoriatedQuantity(self, default=None, *args, **kw):
    """
    Surcharged accessor to calculate the Quantity in second
    from stop date and start date values.
    """
    quantity = self.getQuantity(*args, **kw)
    if quantity in [None, 0]:
      calendar_start_date = self.getStartDate()
      calendar_stop_date = self.getStopDate()
      if (calendar_start_date is not None) and (calendar_stop_date is not None):
        # Convert Days to second
        quantity = abs(int(calendar_stop_date) - int(calendar_start_date))
      else:
        quantity = default
    return quantity

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
    if self.getSource() != None or self.getDestination() != None:
      for period_data in self._getDatePeriodDataList():
        period_data = copy(period_data)
        date_list = [period_data['start_date'], period_data['stop_date']]
        date_list.sort()
        period_data['start_date'] = date_list[1]
        period_data['stop_date'] = date_list[0]
        result.append(self.asContext(self, **period_data))
    return result

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getCalendarPeriodExceptionValueList')
  def getCalendarPeriodExceptionValueList(self):
    """
    Return a list of objects that allows te define exception to the
    current presence period. It could be used for particular
    planned unavailability like banking holidays.
    """
    method = self._getTypeBasedMethod("getCalendarPeriodExceptionValueList")
    if method is None:
      exception_list = self.contentValues(portal_type="Calendar Exception")
    else:
      exception_list = method()
    return exception_list

  def _getDatePeriodDataList(self):
    """
    Get all periods between periodicity start date
    and periodicity stop date
    """
    result = []
    exception_value_list = self.getCalendarPeriodExceptionValueList()
    exception_date_list = [x.getExceptionDate() \
                                       for x in exception_value_list]
    exception_date_list = [x for x in exception_date_list if x is not None]
    exception_date_list.sort()
    if len(exception_date_list) != 0:
      current_exception_date = exception_date_list.pop(0).Date()
    else:
      current_exception_date = None

    start_date = self.getStartDate()
    if start_date is not None:
      stop_date = self.getStopDate(start_date)
      periodicity_stop_date = self.getPeriodicityStopDate(
                                          start_date)
      duration = stop_date - start_date
      if duration > 0:
        # First date has to respect the periodicity config
        next_start_date = self.getNextPeriodicalDate(addToDate(start_date, day=-1))
        while (next_start_date is not None) and \
          (next_start_date <= periodicity_stop_date):

          # Check that next_start_date is not an exception
          if (current_exception_date is not None) and \
             (current_exception_date == next_start_date.Date()):
              # We match an exception date
              # So, don't return this value
              # Update the next exception date
              if len(exception_date_list) != 0:
                current_exception_date = exception_date_list.pop(0).Date()
              else:
                current_exception_date = None
          elif (current_exception_date is not None) and \
             (current_exception_date < next_start_date.Date()):
            # SQL method don't like iterator
  #             yield (next_start_date, next_start_date+duration)
            result.append({'start_date': next_start_date,
                           'stop_date': next_start_date + duration,
                           'quantity': self.getQuantity()})
            # Update the next exception date
            if len(exception_date_list) != 0:
              current_exception_date = exception_date_list.pop(0).Date()
            else:
              current_exception_date = None
          else:
            # SQL method don't like iterator
  #             yield (next_start_date, next_start_date+duration)
            result.append({'start_date': next_start_date,
                           'stop_date': next_start_date + duration,
                           'quantity': self.getQuantity()})
          next_start_date = self.getNextPeriodicalDate(next_start_date)

    return result

  def getNextPeriodicalDate(self, current_date, next_start_date=None):
    """
    Get the next date where this periodic event should start.

    XXX It completely reimplements the PeriodictyMixin method because
    the minimal duration between dates is day, and not minute
    Better way would be to improve the API of getNextPeriodicalDate,
    and optimize addToDate method.
    """
    # XXX Copy/Paste from PeriodicityMixin
    if next_start_date is None:
      next_start_date = current_date
    if next_start_date > current_date:
      return
    else:
      # Make sure the old date is not too far away
      day_count = int(current_date-next_start_date)
      next_start_date = next_start_date + day_count

    timezone = self._getTimezone(next_start_date)
    next_start_date = self._getNextDay(next_start_date, timezone)
    while 1:
      if (self._validateDay(next_start_date)) and \
         (self._validateWeek(next_start_date)) and \
         (self._validateMonth(next_start_date)):
        break
      else:
        next_start_date = self._getNextDay(next_start_date, timezone)

    return DateTime(
      next_start_date.year(),
      next_start_date.month(),
      next_start_date.day(),
      current_date.hour(),
      current_date.minute(),
      current_date.second(),
      timezone)
