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
                      )

    # CMF Factory Type Information
    factory_type_information = \
      {    'id'             : portal_type
         , 'meta_type'      : meta_type
         , 'description'    : """\
An ERP5 Alarm is used in order to check many things from time to time"""
         , 'icon'           : 'rule_icon.gif'
         , 'product'        : 'ERP5Type'
         , 'factory'        : 'addAlarm'
         , 'immediate_view' : 'Alarm_view'
         , 'allow_discussion'     : 1
         , 'allowed_content_types': ()
         , 'filter_content_types' : 1
         , 'global_allow'   : 1
         , 'actions'        :
        ( { 'id'            : 'view'
          , 'name'          : 'View'
          , 'category'      : 'object_view'
          , 'action'        : 'Alarm_view'
          , 'permissions'   : (
              Permissions.View, )
          },
        )
      }

    security.declareProtected(Permissions.View, 'isActive')
    def isActive(self):
      """
      This method returns only 1 or 0. It simply tells if this alarm is currently
      active or not. It is activated when it is doing some calculation with
      activeSense or solve.
      """
      pass

    security.declareProtected(Permissions.ModifyPortalContent, 'activeSense')
    def activeSense(self):
      """
      This method checks if there is a problem. This method can launch a very long
      activity. We don't care about the response, we just want to start
      some calculations. Results should be read with the method 'sense'
      later.
      
      """
      pass

    security.declareProtected(Permissions.ModifyPortalContent, 'sense')
    def sense(self):
      """
      This method returns 0 or 1. 0 for no problem, 1 for problem.
      
      respond if there is a problem. This method should respond quickly.
      Basically the response depends on some previous calculation made by
      activeSense.
      """
      pass

    security.declareProtected(Permissions.View, 'report')
    def report(self):
      """
      This methods produces a report (HTML) 
      This generate the output of the results. It can be used to nicely
      explain the problem. We don't do calculation at this time, it should
      be made by activeSense.
      """
      pass

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

