##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
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
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.DublinCore
                      , PropertySheet.Periodicity
                      )

    security.declareProtected(Permissions.View, 'setNextAlarmDate')
    def setNextAlarmDate(self,current_date=None):
      """
      Get the next date where this periodic event should start.

      We have to take into account the start date, because
      sometimes an event may be started by hand. We must be
      sure to never forget to start an event, event with some
      delays.

      Here are some rules :
      - if the periodicity start date is in the past and we never starts
        this periodic event, then return the periodicity start date.
      - if the periodicity start date is in the past but we already
        have started the periodic event, then see 
      """

      if self.getPeriodicityStartDate() is None:
        return
      next_start_date = self.getAlarmDate()
      if current_date is None: 
        # This is usefull to set the current date as parameter for
        # unit testing, by default it should be now
        current_date = DateTime()
      if next_start_date > current_date:
        return

      def validateHour(self,date):
        periodicity_hour_frequency = self.getPeriodicityHourFrequency()
        periodicity_hour_list = self.getPeriodicityHourList()
        if periodicity_hour_frequency is None and periodicity_hour_list in ([],None,()):
          return 1
        if periodicity_hour_frequency not in ('',None):
          return (date.hour() % periodicity_hour_frequency) == 0
        elif len(periodicity_hour_list)>0:
          return date.hour() in periodicity_hour_list

      def validateDay(self,date):
        periodicity_day_frequency = self.getPeriodicityDayFrequency()
        periodicity_month_day_list = self.getPeriodicityMonthDayList()
        if periodicity_day_frequency is None and periodicity_month_day_list in ([],None,()):
          return 1
        if periodicity_day_frequency not in ('',None):
          return (date.day() % periodicity_day_frequency) == 0
        elif len(periodicity_month_day_list)>0:
          return date.day() in periodicity_month_day_list

      def validateWeek(self,date):
        periodicity_week_frequency = self.getPeriodicityWeekFrequency()
        periodicity_week_day_list = self.getPeriodicityWeekDayList()
        if periodicity_week_frequency is None and periodicity_week_day_list in ([],None,()):
          return 1
        if periodicity_week_frequency not in ('',None):
          return (date.week() % periodicity_week_frequency) == 0
        else:
          return date.Day() in periodicity_week_day_list

      def validateMonth(self,date):
        periodicity_month_frequency = self.getPeriodicityMonthFrequency()
        periodicity_month_list = self.getPeriodicityMonthList()
        if periodicity_month_frequency is None and periodicity_month_list in ([],None,()):
          return 1
        if periodicity_month_frequency not in ('',None):
          return (date.month() % periodicity_month_frequency) == 0
        elif len(periodicity_month_list)>0:
          return date.month() in periodicity_month_list

      next_start_date = addToDate(next_start_date,hour=1)
      while not( next_start_date >= current_date \
                 and validateHour(self,next_start_date) \
                 and validateDay(self,next_start_date) \
                 and validateWeek(self,next_start_date) \
                 and validateMonth(self,next_start_date)):
        next_start_date = addToDate(next_start_date,hour=1)

      self.setAlarmDate(next_start_date)


    security.declareProtected(Permissions.View, 'getWeekDayList')
    def getAlarmDate(self):
      """
      returns something like ['Sunday','Monday',...]
      """
      alarm_date = self._baseGetAlarmDate()
      if alarm_date is None:
        alarm_date = self.getPeriodicityStartDate()
      return alarm_date


    # XXX May be we should create a Date class for following methods ???

    security.declareProtected(Permissions.View, 'getWeekDayList')
    def getWeekDayList(self):
      """
      returns something like ['Sunday','Monday',...]
      """
      return DateTime._days

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
      LOG('getPeriodicityWeekDayList',0,'we should order')
      day_list = self._baseGetPeriodicityWeekDayList()
      new_list = []
      for day in self.getWeekDayList():
        if day_list is not None:
          if day in day_list:
            new_list += [day]
      return new_list



