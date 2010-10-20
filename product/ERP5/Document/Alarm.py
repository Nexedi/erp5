# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004,2007,2009 Nexedi SA and Contributors. All Rights Reserved.
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

from compiler.consts import CO_VARKEYWORDS
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from DateTime import DateTime
from Products.ERP5Type.Message import Message
from Products.ERP5Type.DateUtils import addToDate, atTheEndOfPeriod
from Products.ERP5Security.ERP5UserManager import SUPER_USER
from AccessControl.SecurityManagement import getSecurityManager, \
            setSecurityManager, newSecurityManager

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
    # This method provides an utility to deal with a timezone as a workaround.
    # This is necessary because DateTime does not respect the real timezone
    # such as Europe/Paris, but only stores a difference from GMT such as
    # GMT+1, thus it does not work nicely with daylight savings.
    if date.tzoffset() == 0:
      # Looks like using GMT.
      return date.timezone()
    return None

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
    if next_start_date > current_date \
          or (periodicity_stop_date is not None \
              and next_start_date >= periodicity_stop_date):
      return None

    timezone = self._getTimezone(next_start_date)
    previous_date = next_start_date
    next_start_date = max(self._getNextMinute(next_start_date, timezone),
            current_date)
    while 1:
      if not self._validateMonth(next_start_date):
        next_start_date = self._getNextMonth(next_start_date, timezone)
      elif not (self._validateDay(next_start_date) and
                self._validateWeek(next_start_date)):
        next_start_date = self._getNextDay(next_start_date, timezone)
      elif not self._validateMinute(next_start_date, previous_date):
        next_start_date = self._getNextMinute(next_start_date, timezone)
      elif not self._validateHour(next_start_date):
        next_start_date = self._getNextHour(next_start_date, timezone)
      else:
        parts = list(next_start_date.parts())
        parts[5] = previous_date.second() # XXX keep old behaviour
        parts[6] = timezone
        return DateTime(*parts)

  # XXX May be we should create a Date class for following methods ???
  security.declareProtected(Permissions.AccessContentsInformation, 'getWeekDayList')
  def getWeekDayList(self):
    """
    returns something like ['Sunday','Monday',...]
    """
    return DateTime._days

  security.declareProtected(Permissions.AccessContentsInformation, 'getWeekDayItemList')
  def getWeekDayItemList(self):
    """
    returns something like [('Sunday', 'Sunday'), ('Monday', 'Monday'),...]
    """
    return [(Message(domain='erp5_ui', message=x), x) \
            for x in self.getWeekDayList()]

  security.declareProtected(Permissions.AccessContentsInformation, 'getWeekDayItemList')
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

class Alarm(XMLObject, PeriodicityMixin):
  """
  An Alarm is in charge of checking anything (quantity of a certain
  resource on the stock, consistency of some order,....) periodically.
  This check can span over multiple activities through an active
  process.

  An Alarm is capable of displaying the last result of the check
  process which was run in background. The result can be provided
  either as a boolean value (alarm was raised or not) or 
  in the form of an HTML report which is intended to be 
  displayed in a control center. Moreover, user may be notified
  automatically of alarm failures.

  Alarm may also provide a solution if something wrong happens. This
  solution takes the form of a script which can be invoked
  by the administrator or by the user by clicking on a button
  displayed in the Alarm control center.
  """

  # CMF Type Definition
  meta_type = 'ERP5 Alarm'
  portal_type = 'Alarm'
  add_permission = Permissions.AddPortalContent

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
                    , PropertySheet.Configurable
                    , PropertySheet.Alarm
                    )

  security.declareProtected(Permissions.AccessContentsInformation, 'isActive')
  def isActive(self):
    """
    This method returns only True or False. 
    It simply tells if this alarm is currently
    active or not. An Alarm is said to be active whenever
    some calculation is undergoing either as part
    of the sensing process (activeSense) or as part
    of the problem resolution process (solve).
    """
    return self.hasActivity(only_valid=1)

  def __getTag(self, new):
    # Tag is generated from portal_ids so that it can be retrieved
    # later when creating an active process for example
    portal_ids = self.getPortalObject().portal_ids
    if new:
      id = portal_ids.generateNewId(id_generator='uid', id_group=self.getId())
    else:
      id = portal_ids.getLastLengthGeneratedId(id_group=self.getId())
    return '%s_%s' % (self.getRelativeUrl(), id)

  security.declareProtected(Permissions.AccessContentsInformation, 'activeSense')
  def activeSense(self, fixit=0, params=None):
    """
    This method launches the sensing process as activities.
    It is intended to launch a very long process made
    of many activities. It returns nothing since the results
    are collected in an active process.

    The result of the sensing process can be obtained by invoking
    the sense method or by requesting a report.
    """
    portal_membership = self.getPortalObject().portal_membership
    if fixit or not self.getEnabled():
      checkPermission = portal_membership.checkPermission
      if not checkPermission(Permissions.ManagePortal, self):
        raise Unauthorized('fixing problems or activating a disabled alarm is not allowed')

    # Switch to the superuser temporarily, so that the behavior would not
    # change even if this method is invoked by random users.
    sm = getSecurityManager()
    newSecurityManager(None, portal_membership.getMemberById(SUPER_USER))
    try:
      # Set the next date at which this method should be invoked
      self.setNextAlarmDate()

      # Find the active sensing method and invoke it
      # as an activity so that we can benefit from
      # distribution of alarm processing as soon as possible
      method_id = self.getActiveSenseMethodId()
      if method_id not in (None, ''):
        # A tag is provided as a parameter in order to be
        # able to notify the user after all processes are ended
        # We do some inspection to keep compatibility
        # (because fixit and tag were not set previously)
        tag = self.__getTag(True)
        method = getattr(self, method_id)
        func_code = method.func_code
        try:
          has_kw = func_code.co_flags & CO_VARKEYWORDS
        except AttributeError:
          # XXX guess presence of *args and **kw
          name_list = func_code.co_varnames[func_code.co_argcount:]
          has_args = int(name_list and name_list[0] == 'args')
          has_kw = int(len(name_list) > has_args and
                       name_list[has_args] == 'kw')
        name_list = func_code.co_varnames[:func_code.co_argcount]
        if 'params' in name_list or has_kw:
          # New New API
          getattr(self.activate(tag=tag), method_id)(fixit=fixit, tag=tag, params=params)
        elif 'fixit' in name_list:
          # New API - also if variable number of named parameters
          getattr(self.activate(tag=tag), method_id)(fixit=fixit, tag=tag)
        else:
          # Old API
          getattr(self.activate(tag=tag), method_id)()
        if self.isAlarmNotificationMode():
          self.activate(after_tag=tag).notify(include_active=True, params=params)
    finally:
      # Restore the original user.
      setSecurityManager(sm)

  security.declareProtected(Permissions.ManagePortal, 'sense')
  def sense(self, process=None):
    """
    This method returns True or False. False for no problem, True for problem.

    This method should respond very quickly.

    Complex alarms should use activity based calculations through
    the activeSense method.

    The process parameter can be used to retrive sense values for 
    past processes.
    If it is None, it will return the status of last completed active result.
    """
    method_id = self.getSenseMethodId()
    if process is None:
      process = self.getLastActiveProcess()

    # First case - simple cron style alarm
    # with no results
    if process is None and method_id in (None, ''):
      return None

    # Second case - this alarm does not use an
    # active process. This is perfectly acceptable
    # in some cases, whenever the sense calculation
    # is really fast.
    if process is None:
      method = getattr(self, method_id)
      return method()

    # Third case - this alarm uses an
    # active process and a method_id is defined
    if method_id not in (None, ''):
      method = getattr(self, method_id)
      return method(process=process)

    # Fourth case - this alarm uses an
    # active process but no method_id is defined
    for result in process.getResultList():
      # This is useful is result is returned as a Return instance
      if result.severity > result.INFO:
        return True
      # This is the default case
      if getattr(result, 'result', False):
        return True

    return False
    # This comment here is kept for historical reasons
    # There used to be a call to process.setSenseValue(value)
    # This means that each time an alarm is displayed,
    # we modify it to keep its latest sense result somewhere
    # This was bad for two reasons: first of all, it is
    # actually a caching problem, and if necesssary,
    # this caching problem should be solved by using caches.
    # Then, if caching is required, it may not only be
    # at display time and not only for sense(). So, the
    # baseline is to use caches and if necessary to develop
    # a new cache plugin which uses ZODB to store values
    # for a long time.

  security.declareProtected(Permissions.View, 'report')
  def report(self, reset=0, process=None):
    """
    This methods produces a report (HTML) to display
    the results of the sensing process.

    The report is intended to provide a nice visualisation
    of the sensing process, of problems which may occur or
    of the fact that there was no problem. No calculation
    should be made normally at this time (or very fast calculation).
    Complex alarms should implement calculation through
    the invocation of activeSense.

    Report implementation is normally made using an
    ERP5 Form.
    """
    if process is None:
      process = self.getLastActiveProcess().getRelativeUrl()
    elif not isinstance(process, basestring):
      process = process.getRelativeUrl()
    return self._renderDefaultView('report', process=process, reset=reset)

  security.declareProtected(Permissions.ManagePortal, 'solve')
  def solve(self):
    """
    This method tries resolve a problems detected by an Alarm
    within the sensing process. Problem resolution is
    implemented by an external script.

    If no external script is dehfined, activeSense is invoked 
    with fixit=1
    """
    method_id = self.getSolveMethodId()
    if method_id not in (None, ''):
      method = getattr(self.activate(), method_id)
      return method()
    return self.activeSense(fixit=1)

  security.declareProtected(Permissions.ManagePortal, 'notify')
  def notify(self, include_active=False, params=None):
    """
    This method is called to notify people that some alarm has
    been sensed. Notification consists of sending an email
    to the system address if nothing was defined or to 
    notify all agents defined on the alarm if specified.
    """
    notification_mode = self.getAlarmNotificationMode()
    if notification_mode == 'never':
      return
    # Grab real latest result. Otherwise, we would check n-1 execution as n is
    # still considered running, and its result would be skipped.
    active_process = self.getLastActiveProcess(include_active=include_active)
    sense_result = self.sense(process=active_process)
    if not sense_result and notification_mode != 'always':
        return

    # If a notification method is specified explicitly, call it instead of
    # using the default notification.
    method_id = self.getNotificationMethodId()
    if method_id:
      getattr(self, method_id)(process=active_process,
                               sense_result=sense_result,
                               params=params)
      return

    if sense_result:
      prefix = 'ERROR'
    else:
      prefix = 'INFO'

    notification_tool = getToolByName(self, 'portal_notifications')
    candidate_list = self.getDestinationValueList()
    if not candidate_list:
      candidate_list = None
    result_list = [x for x in active_process.getResultList() if x is not None]
    attachment_list = []
    if len(result_list):
      def sort_result_list(a, b):
        result = - cmp(a.severity, b.severity)
        if result == 0:
          result = cmp(a.summary, b.summary)
        return result
      result_list.sort(sort_result_list)
      rendered_alarm_result_list = ['%02i summary: %s\n%s\n----' %
        (int(getattr(x, 'severity', 0)), getattr(x, 'summary', ''), getattr(x, 'detail', ''))
        for x in result_list]
      rendered_alarm_result = '\n'.join(rendered_alarm_result_list)
      attachment_list.append({'name': 'alarm_result.txt',
                              'content': rendered_alarm_result,
                              'mime_type': 'text/plain'})

    notification_tool.sendMessage(recipient=candidate_list, 
                subject='[%s][%s] Alarm Notification: %s' %
                  (prefix, self.getPortalObject().getTitle(), self.getTitle()),
                message="""
Alarm Title: %s (%s)

Alarm Description:
%s

Alarm Tool Node: %s
""" % (self.getTitle(), self.getId(), self.getDescription(),
       self.getPortalObject().portal_alarms.getAlarmNode()),
                attachment_list=attachment_list)

  security.declareProtected(Permissions.ManagePortal, 'getLastActiveProcess')
  def getLastActiveProcess(self, include_active=False):
    """
    This returns the last active process finished. So it will
    not returns the current one
    """
    if include_active:
      limit = 1
    else:
      limit = self.isActive() and 2 or 1
    active_process_list = self.getPortalObject().portal_catalog(
      portal_type='Active Process', limit=limit,
      sort_on=(('creation_date', 'DESC'),
               # XXX Work around poor resolution of MySQL dates.
               ('CONVERT(`catalog`.`id`, UNSIGNED)', 'DESC')),
      causality_uid=self.getUid())
    if len(active_process_list) < limit:
      process = None
    else:
      process = active_process_list[-1].getObject()
    return process

  security.declareProtected(Permissions.ManagePortal, 
                            'newActiveProcess')
  def newActiveProcess(self, **kw):
    """
    We will create a new active process in order to store
    new results, then this process will be added to the list
    of processes
    """
    activate_kw = kw.get('activate_kw', {})
    activate_kw.setdefault('tag', self.__getTag(False))
    portal_activities = getToolByName(self,'portal_activities')
    active_process = portal_activities.newActiveProcess(start_date=DateTime(),
                                                        causality_value=self,
                                                        activate_kw=activate_kw,
                                                        **kw)
    return active_process

  security.declareProtected(Permissions.ModifyPortalContent, 'setNextAlarmDate')
  def setNextAlarmDate(self, current_date=None):
    """Save the next alarm date.
    """
    alarm_date = self.getAlarmDate()
    if alarm_date is not None:
      if current_date is None:
        # This is usefull to set the current date as parameter for
        # unit testing, by default it should be now
        current_date = DateTime()
      alarm_date = self.getNextPeriodicalDate(current_date, 
                                              next_start_date=alarm_date)
    self.Alarm_zUpdateAlarmDate(uid=self.getUid(), alarm_date=alarm_date)

  security.declareProtected(Permissions.AccessContentsInformation, 'getAlarmDate')
  def getAlarmDate(self):
    """Obtain the next alarm date.
    
    Return a DateTime object which specifies when this alarm should
    be invoked at next time. The return value can be None when it should
    not be invoked automatically.

    By definition, if periodicity start date is not defined (i.e. None),
    their is no valid time range, so return None. If periodicity stop
    date is not defined (i.e. None), assume that this alarm will be
    effective forever. Otherwise, if a date exceeds the periodicity stop
    date, return None, as it is not effective any longer.
    """
    alarm_date = None
    enabled = self.getEnabled()
    periodicity_start_date = self.getPeriodicityStartDate()
    if enabled and periodicity_start_date is not None:
      # Respect what is stored in the catalog.
      result_list = self.Alarm_zGetAlarmDate(uid=self.getUid())
      if len(result_list) == 1:
        alarm_date = result_list[0].alarm_date
      # But if the catalog does not have a valid one, replace it
      # with the start date.
      if alarm_date is None or alarm_date < periodicity_start_date:
        alarm_date = periodicity_start_date

      # Check if it is valid.
      periodicity_stop_date = self.getPeriodicityStopDate()
      if periodicity_stop_date is not None \
            and alarm_date >= periodicity_stop_date:
        alarm_date = None
      else:
        # convert the date to the user provided timezone
        alarm_zone = periodicity_start_date.timezone()
        alarm_date = alarm_date.toZone(alarm_zone)

    return alarm_date

  # XXX there seem to be something which wants to call setters against
  # alarm_date, but alarms do not want to store a date in ZODB.
  security.declareProtected(Permissions.ModifyPortalContent, 'setAlarmDate')
  def setAlarmDate(self, *args, **kw):
    pass

  def _setAlarmDate(self, *args, **kw):
    pass
