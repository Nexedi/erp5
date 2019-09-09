# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2011 Nexedi SA and Contributors. All Rights Reserved.
#                    Francois-Xavier Algrain <fxalgrain@tiolive.com>
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
"""Receive or send SMS"""

#Import python module
import random
import string
from DateTime import DateTime

#Import Zope module
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import  getSecurityManager, \
                                              setSecurityManager, \
                                              newSecurityManager
import zope.interface

from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.XMLObject import XMLObject
from Products import ERP5Security

from erp5.component.interface.ISmsSendingGateway import ISmsSendingGateway
from erp5.component.interface.ISmsReceivingGateway import ISmsReceivingGateway

class DummyGateway(XMLObject):

    """Dummy SMS Gateway Implementation"""
    meta_type='Dummy Gateway'
    portal_type = 'Dummy Gateway'
    security = ClassSecurityInfo()


    add_permission = Permissions.AddPortalContent

    zope.interface.implements(
        ISmsSendingGateway,
        ISmsReceivingGateway)

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.Reference
                      , PropertySheet.SMSGateway
                      )

    security.declareProtected(Permissions.ManagePortal, 'send')
    def send(self, text, recipient, sender):
      """Send a short message.
      """
      #Send message (or test)
      if self.isSimulationMode():
        return None
      return self._generateRandomMessageId()

    security.declareProtected(Permissions.ManagePortal, 'getMessageStatus')
    def getMessageStatus(self, message_id):
      """Retrive the status of a message"""
      return "delivered"

    security.declarePublic('receive')
    def receive(self,REQUEST):
      """Receive push notification from the gateway"""

      #Get current user
      sm = getSecurityManager()
      try:
        #Use SUPER_USER
        portal_membership = self.getPortalObject().portal_membership
        newSecurityManager(None, portal_membership.getMemberById(ERP5Security.SUPER_USER))

        #Dummy notify only new SMS
        self.notifyReception(REQUEST.get("sender"),
                             REQUEST.get("text"),
                             self._generateRandomMessageId())
      finally:
        #Restore orinal user
        setSecurityManager(sm)



    security.declareProtected(Permissions.ManagePortal, 'notifyReception')
    def notifyReception(self, sender, text, message_id):
      """The gateway inform what we ha a new message.
      """

      #Convert phone as erp5 compliant
      def parsePhoneNumber(number):
        #XXX: Should register well formatted number or brut number ?
        #return number
        return "+%s(%s)-%s" % (number[0:2],0,number[2:])


      #Create the new sms in activities
      self.activate(activity='SQLQueue').SMSTool_pushNewSMS(
                              message_id=message_id,
                              sender=parsePhoneNumber(sender),
                              recipient=None,
                              text_content=text,
                              message_type='text/plain',
                              reception_date=DateTime())

    def _generateRandomMessageId(self):
      letters = random.sample(string.ascii_lowercase,20)
      return "%s-%s-%s-%s" % (''.join(letters[0:5]),
                              ''.join(letters[5:10]),
                              ''.join(letters[10:15]),
                              ''.join(letters[15:20]))
