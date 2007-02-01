##############################################################################
#
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Base import Base
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from Products.ERP5Type.DateUtils import addToDate
from Products.ERP5Type.Message import Message

from zLOG import LOG

class Periodicity(Base):
    """
    An Alarm is in charge of checking anything (quantity of a certain
    resource on the stock, consistency of some order,....) periodically.

    It should also provide a solution if something wrong happens.

    Some information should be displayed to the user, and also notifications.
    """

    # CMF Type Definition
    meta_type = 'ERP5 Periodicity'
    portal_type = 'Periodicity'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.DublinCore
                      , PropertySheet.Periodicity
                      )

    def validateMinute(self, date, previous_date):
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

    def validateHour(self, date):
      periodicity_hour_frequency = self.getPeriodicityHourFrequency()
      periodicity_hour_list = self.getPeriodicityHourList()
      if (periodicity_hour_frequency is None) and \
         (periodicity_hour_list in ([], None, ())):
        return 1
      if periodicity_hour_frequency not in ('', None):
        return (date.hour() % periodicity_hour_frequency) == 0
      elif len(periodicity_hour_list) > 0:
        return date.hour() in periodicity_hour_list

    def validateDay(self, date):
      periodicity_day_frequency = self.getPeriodicityDayFrequency()
      periodicity_month_day_list = self.getPeriodicityMonthDayList()
      if (periodicity_day_frequency is None) and \
         (periodicity_month_day_list in ([], None, ())):
        return 1
      if periodicity_day_frequency not in ('', None):
        return (date.day() % periodicity_day_frequency) == 0
      elif len(periodicity_month_day_list) > 0:
        return date.day() in periodicity_month_day_list

    def validateWeek(self, date):
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

    def validateMonth(self, date):
      periodicity_month_frequency = self.getPeriodicityMonthFrequency()
      periodicity_month_list = self.getPeriodicityMonthList()
      if (periodicity_month_frequency is None) and \
         (periodicity_month_list in ([], None, ())):
        return 1
      if periodicity_month_frequency not in ('', None):
        return (date.month() % periodicity_month_frequency) == 0
      elif len(periodicity_month_list) > 0:
        return date.month() in periodicity_month_list

    def getNextAlarmDate(self, current_date, next_start_date=None):
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
      """
      if next_start_date is None:
        next_start_date = current_date
      if next_start_date > current_date:
        return
      else:
        # Make sure the old date is not too far away
        nb_days = int(current_date-next_start_date)
        next_start_date = next_start_date + nb_days

      previous_date = next_start_date
      next_start_date = addToDate(next_start_date, minute=1)
      while 1:
        validate_minute = self.validateMinute(next_start_date, previous_date)
        validate_hour = self.validateHour(next_start_date)
        validate_day = self.validateDay(next_start_date)
        validate_week = self.validateWeek(next_start_date)
        validate_month = self.validateMonth(next_start_date)
        if (next_start_date >= current_date \
            and validate_minute and validate_hour and validate_day \
            and validate_week and validate_month):
          break
        else:
          if not(validate_minute):
            next_start_date = addToDate(next_start_date, minute=1)
          else:
            if not(validate_hour):
              next_start_date = addToDate(next_start_date, hour=1)
            else:
              if not(validate_day and validate_week and validate_month):
                next_start_date = addToDate(next_start_date, day=1)
              else:
                # Everything is right, but the date is still not bigger
                # than the current date, so we must continue
                next_start_date = addToDate(next_start_date, minute=1)
      return next_start_date

    security.declareProtected(Permissions.View, 'setNextAlarmDate')
    def setNextAlarmDate(self, current_date=None):
      """
      Save the next alarm date
      """
      if self.getPeriodicityStartDate() is None:
        return
      next_start_date = self.getAlarmDate()
      if current_date is None:
        # This is usefull to set the current date as parameter for
        # unit testing, by default it should be now
        current_date = DateTime()

      next_start_date = self.getNextAlarmDate(current_date, 
                                              next_start_date=next_start_date)
      if next_start_date is not None:
        self.Alarm_zUpdateAlarmDate(uid=self.getUid(), 
                                    alarm_date=next_start_date)

    security.declareProtected(Permissions.View, 'getAlarmDate')
    def getAlarmDate(self):
      """
      returns something like ['Sunday','Monday',...]
      """
      #alarm_date = self._baseGetAlarmDate()
      #if alarm_date is None:
      #  alarm_date = self.getPeriodicityStartDate()
      alarm_date=None
      result_list = self.Alarm_zGetAlarmDate(uid=self.getUid())
      if len(result_list)==1:
        alarm_date = result_list[0].alarm_date
        periodicity_start_date = self.getPeriodicityStartDate()
        if alarm_date < periodicity_start_date:
          alarm_date = periodicity_start_date
      return alarm_date

    # XXX May be we should create a Date class for following methods ???
    security.declareProtected(Permissions.View, 'getWeekDayList')
    def getWeekDayList(self):
      """
      returns something like ['Sunday','Monday',...]
      """
      return DateTime._days

    security.declareProtected(Permissions.View, 'getWeekDayItemList')
    def getWeekDayItemList(self):
      """
      returns something like [('Sunday', 'Sunday'), ('Monday', 'Monday'),...]
      """
      return [(Message(domain='erp5_ui', message=x), x) \
              for x in self.getWeekDayList()]

    security.declareProtected(Permissions.View, 'getWeekDayItemList')
    def getMonthItemList(self):
      """
      returns something like [('January', 1), ('February', 2),...]
      """
      # DateTime._months return '' as first item
      return [(Message(domain='erp5_ui', message=DateTime._months[i]), i) \
              for i in range(1, len(DateTime._months))]

    # XXX This look like to not works, so override the getter
#    security.declarePrivate('_setPeriodicityWeekDayList')
#    def _setPeriodicityWeekDayList(self,value):
#      """
#      Make sure that the list of days is ordered
#      """
#      LOG('_setPeriodicityWeekDayList',0,'we should order')
#      day_list = self._baseGetPeriodicityWeekDayList()
#      new_list = []
#      for day in self.getWeekDayList():
#        if day in value:
#          new_list += [day]
#      self._baseSetPeriodicityWeekDayList(new_list)

    security.declareProtected(Permissions.View,'getPeriodicityWeekDayList')
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
