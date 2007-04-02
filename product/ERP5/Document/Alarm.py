##############################################################################
#
# Copyright (c) 2004, 2007 Nexedi SARL and Contributors. All Rights Reserved.
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
from Products.ERP5Type.XMLObject import XMLObject
from Products.CMFCore.WorkflowCore import WorkflowMethod
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from Products.ERP5Type.Message import Message
from Products.ERP5Type.DateUtils import addToDate

from zLOG import LOG

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
    if next_start_date is None:
      next_start_date = current_date
    if next_start_date > current_date:
      return
    else:
      # Make sure the old date is not too far away
      day_count = int(current_date-next_start_date)
      next_start_date = next_start_date + day_count

    previous_date = next_start_date
    next_start_date = addToDate(next_start_date, minute=1)
    while 1:
      validate_minute = self._validateMinute(next_start_date, previous_date)
      validate_hour = self._validateHour(next_start_date)
      validate_day = self._validateDay(next_start_date)
      validate_week = self._validateWeek(next_start_date)
      validate_month = self._validateMonth(next_start_date)
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

class Alarm(XMLObject, PeriodicityMixin):
  """
  An Alarm is in charge of checking anything (quantity of a certain
  resource on the stock, consistency of some order,....) periodically.

  It should also provide a solution if something wrong happens.

  Some information should be displayed to the user, and also notifications.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Alarm'
  portal_type = 'Alarm'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Periodicity
                    , PropertySheet.Document
                    , PropertySheet.Task
                    , PropertySheet.Alarm
                    )

  security.declareProtected(Permissions.View, 'isActive')
  def isActive(self):
    """
    This method returns only True or False. 
    It simply tells if this alarm is currently
    active or not. It is activated when it is doing some calculation with
    activeSense or solve.
    """
    return self.hasActivity()

  security.declareProtected(Permissions.ModifyPortalContent, 'activeSense')
  def activeSense(self):
    """
    This method checks if there is a problem. This method can launch a very long
    activity. We don't care about the response, we just want to start
    some calculations. Results should be read with the method 'sense'
    later.

    """
    # Set the new date
    LOG('activeSense, self.getPath()',0,self.getPath())

    self.setNextAlarmDate()
    method_id = self.getActiveSenseMethodId()
    if method_id is not None:
      method = getattr(self.activate(),method_id)
      return method()

  security.declareProtected(Permissions.ModifyPortalContent, 'sense')
  def sense(self):
    """
    This method returns True or False. False for no problem, True for problem.

    This method should respond quickly.  Basically the response depends on some
    previous calculation made by activeSense.
    """
    method_id = self.getSenseMethodId()
    process = self.getLastActiveProcess()
    if process is None:
      return value
    if method_id is not None:
      method = getattr(self,method_id)
      value = method()
    else:
      for result in process.getResultList():
        if result.severity > result.INFO:
          value = True
          break
    process.setSenseValue(value)
    return value

  security.declareProtected(Permissions.View, 'report')
  def report(self, process=None):
    """
    This methods produces a report (HTML)
    This generate the output of the results. It can be used to nicely
    explain the problem. We don't do calculation at this time, it should
    be made by activeSense.
    """
    method_id = self.getReportMethodId(None)
    #LOG('Alarm.report, method_id',0,method_id)
    if method_id is None:
        return ''
    method = getattr(self,method_id)
    process = self.getLastActiveProcess()
    result = None
    if process is not None:
      result = method(process=process)
    return result

  security.declareProtected(Permissions.ModifyPortalContent, 'solve')
  def solve(self):
    """
    This method tries solves the problem detected by sense.

    This solve the problem if there is a problem detected by sense. If
    no problems, then nothing to do here.
    """
    pass

  security.declareProtected(Permissions.ModifyPortalContent, 'notify')
  def _notify(self):
    """
    This method is called to notify people that some alarm has
    been sensed.

    for example we can send email.

    We define nothing here, because we will use an interaction workflow.
    """
    pass

  notify = WorkflowMethod(_notify, id='notify')

  security.declareProtected(Permissions.View, 'getLastActiveProcess')
  def getLastActiveProcess(self):
    """
    This returns the last active process finished. So it will
    not returns the current one
    """
    active_process_list = self.getCausalityRelatedValueList(
                                  portal_type='Active Process')
    def sort_date(a, b):
      return cmp(a.getStartDate(), b.getStartDate())
    active_process_list.sort(sort_date)
    active_process = None
    if len(active_process_list)>0:
      active_process = active_process_list[-1]
    return active_process

  security.declareProtected(Permissions.ModifyPortalContent, 
                            'newActiveProcess')
  def newActiveProcess(self):
    """
    We will create a new active process in order to store
    new results, then this process will be added to the list
    of processes
    """
    portal_activities = getToolByName(self,'portal_activities')
    active_process = portal_activities.newActiveProcess()
    active_process.setStartDate(DateTime())
    active_process.setCausalityValue(self)
    return active_process

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

    next_start_date = self.getNextPeriodicalDate(current_date, 
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
