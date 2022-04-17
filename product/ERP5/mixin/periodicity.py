# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004,2007,2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Globals import InitializeClass
from Products.ERP5Type import Permissions
from Products.ERP5Type.Message import Message

class PeriodicityMixin:
  """
  Periodicity is a Mixin Class used to calculate date periodicity.
  """
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  def _validateMinute(self, date, previous_date):
    """
    Validate if date's minute matches the periodicity definition
    """
    periodicity_minute_frequency = self.getPeriodicityMinuteFrequency()
    periodicity_minute_list = self.getPeriodicityMinuteList()
    if (periodicity_minute_frequency is None) and \
       (periodicity_minute_list in ([], None, ())):
      # in this case, we may want to have an periodicity every hour
      # based on the start date
      # without defining anything about minutes periodicity,
      # so we compare with minutes with the one defined
      # in the previous alarm date
      return (date.minute() == previous_date.minute())
    if periodicity_minute_frequency not in ('', None):
      return (date.minute() % periodicity_minute_frequency) == 0
    elif len(periodicity_minute_list) > 0:
      return date.minute() in periodicity_minute_list

  def _validateHour(self, date):
    """
    Validate if date's hour matches the periodicity definition
    """
    periodicity_hour_frequency = self.getPeriodicityHourFrequency()
    periodicity_hour_list = self.getPeriodicityHourList()
    if (periodicity_hour_frequency is None) and \
       (periodicity_hour_list in ([], None, ())):
      return 1
    if periodicity_hour_frequency not in ('', None):
      return (date.hour() % periodicity_hour_frequency) == 0
    elif len(periodicity_hour_list) > 0:
      return date.hour() in periodicity_hour_list

  def _validateDay(self, date):
    """
    Validate if date's day matches the periodicity definition
    """
    periodicity_day_frequency = self.getPeriodicityDayFrequency()
    periodicity_month_day_list = self.getPeriodicityMonthDayList()
    if (periodicity_day_frequency is None) and \
       (periodicity_month_day_list in ([], None, ())):
      return 1
    if periodicity_day_frequency not in ('', None):
      return (date.day() % periodicity_day_frequency) == 0
    elif len(periodicity_month_day_list) > 0:
      return date.day() in periodicity_month_day_list

  def _validateWeek(self, date):
    """
    Validate if date's week matches the periodicity definition
    """
    periodicity_week_frequency = self.getPeriodicityWeekFrequency()
    periodicity_week_day_list = self.getPeriodicityWeekDayList()
    periodicity_week_list = self.getPeriodicityWeekList()
    if (periodicity_week_frequency is None) and \
       (periodicity_week_day_list in ([], None, ())) and \
       (periodicity_week_list is None):
      return 1
    if periodicity_week_frequency not in ('', None):
      if not((date.week() % periodicity_week_frequency) == 0):
        return 0
    if periodicity_week_day_list not in (None, (), []):
      if not (date.Day() in periodicity_week_day_list):
        return 0
    if periodicity_week_list not in (None, (), []):
      if not (date.week() in periodicity_week_list):
        return 0
    return 1

  def _validateMonth(self, date):
    """
    Validate if date's month matches the periodicity definition
    """
    periodicity_month_frequency = self.getPeriodicityMonthFrequency()
    periodicity_month_list = self.getPeriodicityMonthList()
    if (periodicity_month_frequency is None) and \
       (periodicity_month_list in ([], None, ())):
      return 1
    if periodicity_month_frequency not in ('', None):
      return (date.month() % periodicity_month_frequency) == 0
    elif len(periodicity_month_list) > 0:
      return date.month() in periodicity_month_list

  def _getTimezone(self, date):
    return date.timezone()

  def _getNextMonth(self, date, timezone):
    year = date.year()
    month = date.month()
    if month == 12:
      year += 1
      month = 1
    else:
      month += 1

    return DateTime(year, month, 1, 0, 0, 0, timezone)

  def _getNextDay(self, date, timezone):
    if timezone is not None:
      new_date = DateTime(date.timeTime() + 86400.0, timezone)
    else:
      new_date = DateTime(date.timeTime() + 86400.0)

    # Due to daylight savings, 24 hours later does not always mean that
    # it's next day.
    while new_date.day() == date.day():
      if timezone is not None:
        new_date = DateTime(new_date.timeTime() + 3600.0, timezone)
      else:
        new_date = DateTime(new_date.timeTime() + 3600.0)
    return DateTime(new_date.year(), new_date.month(), new_date.day(),
            0, 0, 0, timezone)

  def _getNextHour(self, date, timezone):
    if timezone is not None:
      new_date = DateTime(date.timeTime() + 3600.0, timezone)
    else:
      new_date = DateTime(date.timeTime() + 3600.0)
    return DateTime(new_date.year(), new_date.month(), new_date.day(),
            new_date.hour(), 0, 0, timezone)

  def _getNextMinute(self, date, timezone):
    if timezone is not None:
      new_date = DateTime(date.timeTime() + 60.0, timezone)
    else:
      new_date = DateTime(date.timeTime() + 60.0)
    return DateTime(new_date.year(), new_date.month(), new_date.day(),
            new_date.hour(), new_date.minute(), 0, timezone)

  security.declareProtected(Permissions.AccessContentsInformation, 'getNextPeriodicalDate')
  def getNextPeriodicalDate(self, current_date, next_start_date=None):
    """
    Get the next date where this periodic event should start.

    We have to take into account the start date, because
    sometimes an event may be started by hand. We must be
    sure to never forget to start an event, even with some
    delays.

    Here are some rules :
    - if the periodicity start date is in the past and we never starts
      this periodic event, then return the periodicity start date.
    - if the periodicity start date is in the past but we already
      have started the periodic event, then see

    XXX Better API is needed. It may defined which minimal time duration has to
    be added in order to calculate next date.
    Ex: here, we use minute as smaller duration.
    On CalendarPeriod, day is the smaller duration.
    """
    periodicity_stop_date = self.getPeriodicityStopDate()
    if next_start_date is None:
      next_start_date = current_date
    if periodicity_stop_date is not None \
        and next_start_date >= periodicity_stop_date:
      return None
    elif next_start_date > current_date:
      return next_start_date

    timezone = self._getTimezone(next_start_date)
    previous_date = next_start_date
    next_start_date = max(self._getNextMinute(next_start_date, timezone),
            current_date)

    # We'll try every date to check if they validate the periodicity
    # constraints, but there might not be any valid date (for example,
    # repeat every 2nd week in August can never be validated). Because
    # gregorian calendar repeat every 28 years, if we did not get a match
    # in the next 28 years we stop looping.
    max_date = next_start_date + (28 * 366)
    while next_start_date < max_date:
      if not self._validateMonth(next_start_date):
        next_start_date = self._getNextMonth(next_start_date, timezone)
      elif not (self._validateDay(next_start_date) and
                self._validateWeek(next_start_date)):
        next_start_date = self._getNextDay(next_start_date, timezone)
      elif not self._validateHour(next_start_date):
        next_start_date = self._getNextHour(next_start_date, timezone)
      elif not self._validateMinute(next_start_date, previous_date):
        next_start_date = self._getNextMinute(next_start_date, timezone)
      else:
        parts = list(next_start_date.parts())
        parts[5] = previous_date.second() # XXX keep old behaviour
        next_start_date = DateTime(*parts)
        if timezone is not None:
          next_start_date = next_start_date.toZone(timezone)
        return next_start_date

  # XXX May be we should create a Date class for following methods ???
  security.declareProtected(Permissions.AccessContentsInformation, 'getWeekDayList')
  def getWeekDayList(self):
    """
    returns something like ['Sunday','Monday',...]
    """
    try:
      from DateTime.DateTime import _DAYS
      return _DAYS
    except ImportError: # BBB DateTime 2.12
      return DateTime._days

  security.declareProtected(Permissions.AccessContentsInformation, 'getWeekDayItemList')
  def getWeekDayItemList(self):
    """
    returns something like [('Sunday', 'Sunday'), ('Monday', 'Monday'),...]
    """
    return [(Message(domain='erp5_ui', message=x), x) \
            for x in self.getWeekDayList()]

  security.declareProtected(Permissions.AccessContentsInformation, 'getMonthItemList')
  def getMonthItemList(self):
    """
    returns something like [('January', 1), ('February', 2),...]
    """
    # DateTime._months return '' as first item
    return [(Message(domain='erp5_ui', message=DateTime._months[i]), i) \
            for i in range(1, len(DateTime._months))]

  security.declareProtected(Permissions.AccessContentsInformation,'getPeriodicityWeekDayList')
  def getPeriodicityWeekDayList(self):
    """
    Make sure that the list of days is ordered
    """
    #LOG('getPeriodicityWeekDayList',0,'we should order')
    day_list = self._baseGetPeriodicityWeekDayList()
    new_list = []
    for day in self.getWeekDayList():
      if day_list is not None:
        if day in day_list:
          new_list += [day]
    return new_list

InitializeClass(PeriodicityMixin)
