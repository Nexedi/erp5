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

    security.declareProtected(Permissions.View, 'getNextStartDate')
    def getNextStartDate(self):
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
      current_date = DateTime()
      # XXX Never store attributes
      #next_start_date = getattr(self,'_next_start_date',None)
      next_start_date = self.getPeriodicityStartDate()
      start_date = self.getStartDate()
      # AXXX never store attributeslready calculated
      #if next_start_date is not None and \
      #    (next_start_date > current_date) or \
      #    (start_date is not None and start_date < next_start_date):
      #  pass
      # simple cases where the next start date will be the periodicity start date
      #elif next_start_date is None and \
      #    (self.getPeriodicityStartDate() > current_date) or \
      #    (self.getStartDate() is None) or \
      #    (self.getStartDate(DateTime()) < self.getPeriodicityStartDate()):
      #  next_start_date = self.getPeriodicityStartDate()
      # We have to do calculation in order to know the next start date
      #else:
      if next_start_date is None:
        next_start_date = self.getPeriodicityStartDate()
      if start_date is None:
        start_date = next_start_date
      periodicity_day = self.getPeriodicityDay()
      periodicity_week = self.getPeriodicityWeek()
      periodicity_month = self.getPeriodicityMonth()
      # Day period
      if periodicity_day not in ('',None):
        next_start_date = next_start_date + periodicity_day
        while start_date > next_start_date:
          next_start_date = next_start_date + periodicity_day
      # Week period
      elif periodicity_week not in ('',None):
        next_start_date = next_start_date + 1
        periodicity_week_day = self.getPeriodicityWeekDay()
        while (next_start_date.strftime('%A').lower() not in periodicity_week_day) and \
            start_date > next_start_date:
          next_start_date = next_start_date + 1
        # If we are at the beginning of a new week, make sure that
        # we take into account the number of week between two periods
        if next_start_date.strftime('%A').lower() == periodicity_week_day[0]:
          next_start_date = next_start_date + 7 * (periodicity_week-1)
      # Month period
      elif periodicity_month not in ('',None):
        pass
        # XXX to be implemented
        #next_start_date = next_start_date + 1
        #periodicity_month_day = self.getPeriodicityWeekDay()
        #if periodicity_month_day is not None:
        #  while
      # XXX never store setattr(self,'_next_start_date',next_start_date)
      return next_start_date


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
        if day in self._baseGetPeriodicityWeekDayList():
          new_list += [day]
      return new_list



