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
import urllib
from DateTime import DateTime

#Import Zope module
from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import  getSecurityManager, \
                                              setSecurityManager, \
                                              newSecurityManager
import zope.interface
from zLOG import LOG, INFO

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products import ERP5Security

#Product Module
from Products.ERP5ShortMessage.Errors import SMSGatewayError


class MobytGateway(XMLObject):

    """Mobyt SMS Gateway Implementation"""
    meta_type='Mobyt Gateway'
    portal_type = 'Mobyt Gateway'
    security = ClassSecurityInfo()

    add_permission = Permissions.AddPortalContent

    zope.interface.implements(interfaces.ISmsGateway)

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properi ties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.Reference
                      , PropertySheet.SMSGateway
                      )

    api_url = "http://multilevel.mobyt.fr/sms"
    security.declarePublic('getAllowedMessageType')
    def getAllowedMessageType(self):
      """List of all message type"""
      return ['text','multitext', 'wappush', 'ucs2', 'multiucs2']

    security.declarePrivate("_fetchSendResponseAsDict")
    def _fetchSendResponseAsDict(self,page):
      """Page result is like Key=value in text format.
         We transform it to a more powerfull dictionnary"""
      result = {}
      lines = page.readlines()
      assert len(lines) == 1, "Multi lines response is not managed %s" % lines
      line = lines[0]
      parts = line.split(' ')
      #Format is 'Status Message'
      result['status'] = parts[0]
      result['status_info'] = ' '.join(parts[1:])

      return result

    security.declarePrivate("_fetchStatusResponseAsDict")
    def _fetchStatusResponseAsDict(self,page):
      """Page result is like Key=value in text format.
         We transform it to a more powerfull dictionnary"""
      result = {}
      lines = page.readlines()

      #First line is special : CSV column title or error inform
      line = lines[0]
      if line[0:1] == "KO":
        result['status'] = "KO"
        result['status_info'] = line[2:]
        return result

      def _cleanText(s):
        return s.replace('\r','').replace('\n','')

      column_name_list = line.split(',')
      column_count = len(column_name_list)
      #Clean last colum
      column_name_list[-1] = _cleanText(column_name_list[-1])

      result['status'] = "OK"
      row_list = []
      #Batch other line to get all status
      for line in lines[1:]:
        row = {}
        column_value_list = line.split(',')
        column_value_list[-1] = _cleanText(column_value_list[-1])
        for i in range(0,column_count):
          row[column_name_list[i]] = column_value_list[i]
        row_list.append(row)

      result['status_info'] = row_list

      return result

    security.declarePrivate("_transformPhoneUrlToGatewayNumber")
    def _transformPhoneUrlToGatewayNumber(self,phone):
      """Transform url of phone number to a valid phone number (gateway side)"""
      phone = phone.replace('tel:', '').replace('(0)','').replace('-','')
      # Check that phone number can not be something not existing
      assert not(phone.startswith('99000'))
      return phone

    security.declareProtected(Permissions.ManagePortal, 'send')
    def send(self, text,recipient,sender=None, sender_title=None,
              message_type="text",test=False,**kw):
      """Send a message.
         Parameters:
         text -- message
         recipient -- phone url of destination_reference. Could be a list
         sender -- phone url of source
         sender_title -- Use it as source if the gateway has title mode enable
         message_type -- Only 'text' is available today
         test -- Force the test mode

         Kw Parameters:
         quality -- Quality of the SMS (default,n)

         Return message id
         """
      #Check messsage type
      if message_type not in self.getAllowedMessageType():
        raise ValueError, "Type of message in not allowed"

      #Check message qualit
      quality = kw.get('quality','n') #Allow sender personalization and status of SMS
      assert quality in ['n','l','ll'], "Unknown quality : '%s'" % quality

      #Recipients
      if not isinstance(recipient, str):
        recipient_count = len(recipient)
        recipient = ",".join([self._transformPhoneUrlToGatewayNumber(x) for x in recipient])
      else:
        recipient = self._transformPhoneUrlToGatewayNumber(recipient)
        recipient_count = 1

      if recipient_count  > 1:
        base_url = self.api_url + "/batch.php" #Multi recipient
      else:
        base_url = self.api_url + "/send.php"

      #Common params
      params = {  "user" : self.getGatewayUser(),
                  "pass" : self.getGatewayPassword(),
                  "rcpt" : recipient,
                  "data" : text,
                  "qty"  : quality,
                  "return_id": 1}

      #Define sender
      if sender_title and self.isTitleMode() and quality == 'n':
        params['sender'] = sender_title
      elif sender:
        params['sender'] = self._transformPhoneUrlToGatewayNumber(sender)
      elif self.getDefaultSender():
        params['sender'] = self.getDefaultSender()

      #Define type of message
      if message_type != "text":
        assert quality == 'n', "This type of message require top level messsage quality"
        assert message_type in self.getAllowedMessageType(), "Unknown message type"
        params['operation'] = message_type.capitalize()

      #Send message (or test)
      if test or self.isSimulationMode():
        LOG("MobytGateway", INFO, params)
        result =  {'status': "Test"}
      else:
        params = urllib.urlencode(params)
        page = urllib.urlopen(base_url, params)
        result = self._fetchSendResponseAsDict(page)

      #Check result and return
      if result['status'] == "OK":
        return [result.get('status_info', "")] #return message id (gateway side)
      elif result['status'] == "KO":
        #we get an error when call the gateway
        raise SMSGatewayError, urllib.unquote(result.get('status_info', "Impossible to send the SMS"))
      elif result['status'] == "Test":
        #just a test, no message id
        return None
      else:
        raise ValueError("Unknown result", 0, result)

    security.declareProtected(Permissions.ManagePortal, 'getMessageStatus')
    def getMessageStatus(self, message_id):
      """Retrive the status of a message"""
      base_url = self.api_url + "/batch-status.php"

      params = {  "user" : self.getGatewayUser(),
                  "pass" : self.getGatewayPassword(),
                  "id" : message_id,
                  "type" : 'notify',
                  "schema" : 1  }

      params = urllib.urlencode(params)
      page = urllib.urlopen(base_url, params)
      result = self._fetchStatusResponseAsDict(page)

      if result['status'] == "OK":
        row_list = result.get('status_info')
        #return only status_text list
        if len(row_list) == 1:
          return row_list[0].get('status_text').lower()
        else:
          status_list = []
          for row in row_list:
            status_list.append(row.get('status_text').lower())
          return status_list

      elif result['status'] == "KO":
        #we get an error when call the gateway
        raise SMSGatewayError, urllib.unquote(result.get('status_info', "Impossible to get the message status"))

    security.declarePublic('receive')
    def receive(self,REQUEST):
      """Receive push notification from the gateway"""

      #Get current user
      sm = getSecurityManager()
      try:
        #Use SUPER_USER
        portal_membership = self.getPortalObject().portal_membership
        newSecurityManager(None, portal_membership.getMemberById(ERP5Security.SUPER_USER))

        #Mobyt notify only new SMS
        self.notifyReception(REQUEST.get("orig"),
                             REQUEST.get("text"),
                             REQUEST.get("ticket"))
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
