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
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.Predicate import Predicate
from Acquisition import aq_base, aq_parent, aq_inner, aq_acquire
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from zLOG import LOG



class Alarm(XMLObject):
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
    security.declareObjectProtected(Permissions.View)

    # Default Properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.CategoryCore
                      , PropertySheet.DublinCore
                      , PropertySheet.Alarm
                      , PropertySheet.Document
                      , PropertySheet.Task
                      , PropertySheet.Periodicity
                      )

    security.declareProtected(Permissions.View, 'isActive')
    def isActive(self):
      """
      This method returns only True or False. It simply tells if this alarm is currently
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
      self.setStartDate(DateTime())
      method_id = self.getActiveSenseMethodId()
      method = getattr(self,method_id)
      return method()

    security.declareProtected(Permissions.ModifyPortalContent, 'sense')
    def sense(self):
      """
      This method returns True or False. False for no problem, True for problem.
      
      respond if there is a problem. This method should respond quickly.
      Basically the response depends on some previous calculation made by
      activeSense.
      """
      method_id = self.getSenseMethodId()
      method = getattr(self,method_id)
      return method()

    security.declareProtected(Permissions.View, 'report')
    def report(self):
      """
      This methods produces a report (HTML) 
      This generate the output of the results. It can be used to nicely
      explain the problem. We don't do calculation at this time, it should
      be made by activeSense.
      """
      method_id = self.getReportMethodId()
      method = getattr(self,method_id)
      return method()

    security.declareProtected(Permissions.ModifyPortalContent, 'solve')
    def solve(self):
      """
      This method tries solves the problem detected by sense.
      
      This solve the problem if there is a problem detected by sense. If
      no problems, then nothing to do here.
      """
      pass

    security.declareProtected(Permissions.ModifyPortalContent, 'notify')
    def notify(self):
      """
      This method is called to notify people that some alarm has 
      been sensed.
      
      for example we can send email.
      """
      pass


    security.declareProtected(Permissions.View, 'getActiveProcessList')
    def getActiveProcessList(self):
      """
      Returns the list of active processes used with
      this alarm. The list of processes will allow to
      retrieve the results history of this alarm
      """
      process_id_list = self.getActiveProcessIdList()
      portal_activities = getToolByName(self,'portal_activities')
      process_list = []
      if process_id_list is not None:
        for process_id in process_id_list:
          process = portal_activities._getOb(process_id)
          process_list.append(process)
      return process_list

    security.declareProtected(Permissions.View, 'getLastActiveProcess')
    def getLastActiveProcess(self):
      """
      This returns the last active process finished. So it will
      not returns the current one
      """
      active_process_id_list = self.getActiveProcessIdList()
      portal_activities = getToolByName(self,'portal_activities')
      last_process = None
      if active_process_id_list is not None:
        if len(active_process_id_list)>0 and not self.isActive():
          last_process_id = active_process_id_list[len(active_process_id_list)-1]
          last_process = portal_activities._getOb(last_process_id)
        elif len(active_process_id_list)>1 and self.isActive():
          last_process_id = active_process_id_list[len(active_process_id_list)-2]
          last_process = portal_activities._getOb(last_process_id)
      return last_process

    security.declareProtected(Permissions.View, 'getCurrentActiveProcess')
    def getCurrentActiveProcess(self):
      """
      Returns the list of active processes used with
      this alarm. The list of processes will allow to
      retrieve the results history of this alarm
      """
      current_process = None
      active_process_id_list = self.getActiveProcessIdList()
      if active_process_id_list is not None:
        if len(active_process_id_list)>0 and self.isActive():
          current_process_id = active_process_id_list[len(active_process_id_list)-1]
          portal_activities = getToolByName(self,'portal_activities')
          current_process = portal_activities._getOb(current_process_id)
      return current_process

    security.declareProtected(Permissions.ModifyPortalContent, 'newActiveProcess')
    def newActiveProcess(self):
      """
      We will create a new active process in order to store
      new results, then this process will be added to the list
      of processes
      """
      portal_activities = getToolByName(self,'portal_activities')
      active_process = portal_activities.newActiveProcess()
      process_id = active_process.getId()
      active_process_id_list = self.getActiveProcessIdList()
      active_process_id_list.append(process_id)
      self.setActiveProcessIdList(active_process_id_list)
      return active_process

    security.declareProtected(Permissions.View, 'getActiveProcessIdList')
    def getActiveProcessIdList(self):
      """
      Returns the list of process ids used to store results of this alarm
      """
      return getattr(self,'_active_process_id_list',[])

    security.declareProtected(Permissions.ModifyPortalContent, 'setActiveProcessIdList')
    def setActiveProcessIdList(self, value):
      """
      Set the list of process ids used to store results of this alarm
      """
      self._active_process_id_list = value
      

