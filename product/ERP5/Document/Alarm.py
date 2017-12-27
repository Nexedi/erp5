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
from random import getrandbits
from Acquisition import aq_base
from DateTime import DateTime
from AccessControl import ClassSecurityInfo, Unauthorized
from AccessControl.SecurityManagement import getSecurityManager, \
            setSecurityManager, newSecurityManager
from AccessControl.User import nobody
from Products.CMFActivity.ActivityRuntimeEnvironment import getActivityRuntimeEnvironment
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5.mixin.periodicity import PeriodicityMixin

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

  security.declareProtected(Permissions.AccessContentsInformation, 'activeSense')
  def activeSense(self, fixit=0, activate_kw=(), params=None):
    """
    This method launches the sensing process as activities.
    It is intended to launch a very long process made
    of many activities. It returns nothing since the results
    are collected in an active process.

    The result of the sensing process can be obtained by invoking
    the sense method or by requesting a report.
    """
    activate_kw = dict(activate_kw)

    if (fixit or not self.getEnabled()) and not self.getPortalObject().portal_membership.checkPermission(Permissions.ManagePortal, self):
      raise Unauthorized('fixing problems or activating a disabled alarm is not allowed')

    # Use UnrestrictedMethod, so that the behaviour would not
    # change even if this method is invoked by random users.
    @UnrestrictedMethod
    def _activeSense():
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
        if 'tag' not in activate_kw:
          # If a given alarm is running more than once at a given point in
          # time, there is a risk that the same random value will have been
          # produced.
          # In such event, notify() will be delayed until all conflicting
          # invocations are done executing.
          # Also, all notifications will as a result refer to a single
          # ActiveProcess, so all but one notification content will be lost to
          # someone only checking notification content.
          # This is expected to be highly unlikely to have any meaningful
          # effect, because:
          # - if a single alarm can be running multiple times in parallel and
          #   has notifications enabled, there is anyway no guarantee that each
          #   payload will actually be properly notified (independently from
          #   any tag collision)
          # - if a single alarm is not usually happening in parallel and
          #   notifications are enabled (hence, there is a reasonable
          #   expectation that each notification will properly happen),
          #   parallel execution means a former invocation failed, so
          #   administrator attention should already be attracted to the issue.
          # - and overall, alarm concurrency should be low enough that
          #   collision should stay extremely low: it should be extremely rare
          #   for a notification-neabled alarm to run even 10 times in parallel
          #   (as alarms can at most be spawned every minute), and even in such
          #   case the probability of a collision is about 2e-9 (10 / 2**32).
          #   Assuming 10 alarms spawned every second with a one-second duration
          #   it takes a bit under 7 years for a single collision to be more
          #   likely to have occurred than not: 50% / (10 / 2**32) = 6.8 years
          # On the other hand, using a completely constant tag per alarm would
          # mean notify() would be blocked by any isolated failure event, which
          # increases the pressure on a timely resolution of what could be a
          # frequent occurrence (ex: an alarm pulling data from a 3rd-party
          # server with poor availability).
          activate_kw['tag'] = '%s_%x' % (self.getRelativeUrl(), getrandbits(32))
        tag = activate_kw['tag']
        method = getattr(self, method_id)
        func_code = method.func_code
        try:
          has_kw = func_code.co_flags & CO_VARKEYWORDS
        except AttributeError:
          # XXX guess presence of *args and **kw
          name_list = func_code.co_varnames[func_code.co_argcount:]
          has_args = bool(name_list and name_list[0] == 'args')
          has_kw = bool(len(name_list) > has_args and
                       name_list[has_args] == 'kw')
        name_list = func_code.co_varnames[:func_code.co_argcount]
        if 'params' in name_list or has_kw:
          # New New API
          getattr(self.activate(**activate_kw), method_id)(fixit=fixit, tag=tag, params=params)
        elif 'fixit' in name_list:
          # New API - also if variable number of named parameters
          getattr(self.activate(**activate_kw), method_id)(fixit=fixit, tag=tag)
        else:
          # Old API
          getattr(self.activate(**activate_kw), method_id)()
        if self.isAlarmNotificationMode():
          self.activate(after_tag=tag).notify(include_active=True, params=params)

    # switch to nobody temporarily so that unrestricted _activeSense
    # is always invoked by system user.
    sm = getSecurityManager()
    newSecurityManager(None, nobody)

    try:
      _activeSense()
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
      if result.isError():
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

  security.declareProtected(Permissions.AccessContentsInformation, 'report')
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

    portal = self.getPortalObject()
    notification_tool = portal.portal_notifications
    candidate_list = []
    domain_type_set = portal.getPortalDomainTypeList()
    for candidate_value in self.getDestinationValueList():
      if candidate_value.getPortalType() in domain_type_set:
        test = candidate_value.test
        for recipient in portal.portal_catalog(
          query=candidate_value.asQuery(),
        ):
          recipient_value = recipient.getObject()
          if test(recipient_value):
            candidate_list.append(recipient_value)
      else:
        candidate_list.append(candidate_value)
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
                  (prefix, portal.getTitle(), self.getTitle()),
                message="""
Alarm Title: %s (%s)

Alarm Description:
%s

Alarm Tool Node: %s
""" % (self.getTitle(), self.getId(), self.getDescription(),
       portal.portal_alarms.getAlarmNode()),
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
    active_process_list = self.getPortalObject().portal_catalog.unrestrictedSearchResults(
      portal_type='Active Process', limit=limit,
      sort_on=(('creation_date', 'DESC'),
               ('id', 'DESC', 'UNSIGNED'),),
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
    activate_kw = kw.pop('activate_kw', {})
    try:
      activity_runtime_environment = getActivityRuntimeEnvironment()
    except KeyError:
      pass
    else:
      activate_kw.setdefault('tag', activity_runtime_environment.getTag())
    return self.getPortalObject().portal_activities.newActiveProcess(
      start_date=DateTime(),
      causality_value=self,
      activate_kw=activate_kw,
      **kw
    )

  security.declareProtected(Permissions.ModifyPortalContent, 'setNextAlarmDate')
  def setNextAlarmDate(self, current_date=None):
    """Save the next alarm date.
    """
    alarm_date = self.getAlarmDate()
    if alarm_date is not None:
      if current_date is None:
        # This is useful to set the current date as parameter for
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
