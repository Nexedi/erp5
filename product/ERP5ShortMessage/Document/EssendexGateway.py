# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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
from lxml import etree
from DateTime import DateTime

#Import Zope module
from AccessControl import ClassSecurityInfo, \
                          Unauthorized
from AccessControl.SecurityManagement import  getSecurityManager, \
                                              setSecurityManager, \
                                              newSecurityManager
import zope.interface
from zLOG import LOG, INFO

from Products.ERP5Type import Permissions, PropertySheet, interfaces
from Products.ERP5Type.XMLObject import XMLObject
from Products import ERP5Security

#Product Module
from Products.ERP5ShortMessage.SMSGatewayError import SMSGatewayError



class EssendexGateway(XMLObject):

    """Base of SMS an Gateway. You can use push notification for delivered and new message notification."""
    meta_type='Essendex Gateway'
    portal_type = 'Essendex Gateway'
    security = ClassSecurityInfo()


    add_permission = Permissions.AddPortalContent

    zope.interface.implements(
        interfaces.ISmsSendingGateway,
        interfaces.ISmsReceivingGateway)

    # Declarative security
    security = ClassSecurityInfo()
    security.declareObjectProtected(Permissions.AccessContentsInformation)

    # Declarative properties
    property_sheets = ( PropertySheet.Base
                      , PropertySheet.XMLObject
                      , PropertySheet.Reference
                      , PropertySheet.SMSGateway
                      )

    api_url = "https://www.esendex.com/secure/messenger/formpost"

    security.declarePrivate("_fetchPageAsDict")
    def _fetchPageAsDict(self,page):
      """Page result is like Key=value in text format.
         We transform it to a more powerfull dictionnary"""
      result = {}
      index = 0

      #Read all lines
      for line in page.readlines():

        #Look is the line have multi key/value
        parts = line.split('&')
        if len(parts) == 1:
          data = parts[0].split('=')
          #Remove \n et \r from value
          result[data[0]] = urllib.unquote(data[1].replace('\r','').replace('\n',''))

        else:
          #Mutil values
          subresult = {}
          for part in parts:
            data = part.split('=')
            subresult[data[0]] = urllib.unquote(data[1].replace('\r','').replace('\n',''))
          result[index] = subresult
          #Increment index for next
          index += 1

      return result

    security.declarePrivate("_transformPhoneUrlToGatewayNumber")
    def _transformPhoneUrlToGatewayNumber(self,phone):
      """Transform url of phone number to a valid phone number (gateway side)"""
      phone = phone.replace('tel:', '').replace('+','').replace('(0)','').replace('-','')
      # Check that phone number can not be something not existing
      assert not(phone.startswith('99000'))
      return phone

    security.declarePrivate("_parsePhoneNumber")
    def _parsePhoneNumber(self,number):
      """Convert phone number for erp5 compliance"""
      return "+%s(%s)-%s" % (number[0:2],0,number[2:])

    security.declarePrivate("_parsePhoneNumber")
    def _parseDate(self, string):
      """Convert a string (like 2011-05-03 10:23:16Z) to a DateTime"""
      return DateTime(string.replace('Z', ' GTM+2'))

    def _convertTimeDeltaToSeconds(self, timedelta):
      """ Convert a timedelta to seconds """
      return timedelta.seconds + (timedelta.days * 24 * 60 * 60)

    security.declareProtected(Permissions.ManagePortal, 'send')
    def send(self, text, recipient, sender):
      """Send a message.
      """
      traverse = self.getPortalObject().restrictedTraverse
      message_type = self.getProperty('essendex_message_type', 'text')
      assert message_type in ('text', 'binary', 'smartMessage', 'unicode')

      validity_period = self.getProperty('essendex_validity_period', 0)

      recipient = self._transformPhoneUrlToGatewayNumber(
          traverse(recipient).getDefaultMobileTelephoneValue().asURL())

      base_url = self.api_url + "/SendSMS.aspx"
      params = {'Username': self.getGatewayUser(),
                'Password': self.getGatewayPassword(),
                'Account': self.getGatewayAccount(),
                'Recipient': recipient,
                'Body': text,
                'Type': message_type.capitalize(),
                'ValidityPeriod': validity_period,
                'PlainText': 1,
                }

      if self.isTitleMode():
        params['Originator'] = traverse(sender).getDefaultMobileTelephoneValue().getTitle()
      else:
        params['Originator'] = self._transformPhoneUrlToGatewayNumber(
            traverse(sender).getDefaultMobileTelephoneValue().asURL()) or self.getDefaultSender()

      if self.isSimulationMode():
        params['Test'] = 1
        LOG("EssendexGateway", INFO, params)

      params = urllib.urlencode(params)
      page = urllib.urlopen(base_url, params)
      result = self._fetchPageAsDict(page)
      if result['Result'] == "OK":
        message_ids = result.get('MessageIDs', "")
        #If a message is sent to multiple recipients, multiple IDs are returned
        #each seperated by a comma.
        return message_ids.split(",")
      elif result['Result'] == "Error":
        #we get an error when call the gateway
        raise SMSGatewayError, urllib.unquote(result.get('Message', "Impossible to send the SMS"))
      elif result['Result'] == "Test":
        #just a test, no message id
        return None
      else:
        raise ValueError("Unknown result", 0, result)

    security.declareProtected(Permissions.ManagePortal, 'getMessageStatus')
    def getMessageStatus(self, message_id):
      """Retrive the status of a message"""
      base_url = self.api_url + "/QueryStatus.aspx"

      params = {'Username': self.getGatewayUser(),
                'Password': self.getGatewayPassword(),
                'Account': self.getGatewayAccount(),
                'PlainText': 1,
                'MessageID': message_id,
                }

      params = urllib.urlencode(params)
      page = urllib.urlopen(base_url, params)
      result = self._fetchPageAsDict(page)

      if result['Result'] == "OK":
        return result.get('MessageStatus').lower()
      elif result['Result'] == "Error":
        #we get an error when call the gateway
        raise SMSGatewayError, urllib.unquote(result.get('Message', "Impossible to get the message status"))

    security.declarePublic('receive')
    def receive(self, REQUEST, **kw):
      """Receive push notification"""

      #XML is stored is BODY of request
      datas = REQUEST['BODY']

      if not datas:
        raise SMSGatewayError, "Impossible to notify nothing"

      #Get current user
      sm = getSecurityManager()
      try:
        #Use SUPER_USER
        portal_membership = self.getPortalObject().portal_membership
        newSecurityManager(None, portal_membership.getMemberById(ERP5Security.SUPER_USER))

        #Parse XML
        root = etree.fromstring(datas)

        #Choice action corresponding to the notification type
        notification_type =  root.tag

        #Parse text XML Element to dict
        xml = {}
        for child in root.getchildren():
          xml[child.tag] = child.text

        #Check Account id
        if xml['AccountId'] != self.getGatewayAccountId():
          raise Unauthorized, 'Bad accound id (%s)' % xml['AccountId']

        if notification_type == 'InboundMessage':
          self.notifyReception(xml)
        elif notification_type == 'MessageDelivered':
          self.notifyDelivery(xml)
        elif notification_type == 'MessageError':
          raise SMSGatewayError, "'MessageError' notification is not implemented (%s)" % str(kw)
        elif notification_type == 'SubscriptionEvent':
          raise SMSGatewayError, "'MessageError' notification is not implemented (%s)" % str(kw)
        else:
          raise SMSGatewayError, "Unknow '%s' notification (%s)" % (notification_type, str(kw))
      finally:
        #Restore orinal user
        setSecurityManager(sm)


    security.declareProtected(Permissions.ManagePortal, 'notifyReception')
    def notifyReception(self, xml):
      """The gateway inform what we ha a new message.
         root: lxml Element"""

      """
      <InboundMessage>
        <Id>{guid-of-push-notification}</Id>
        <MessageId>{guid-of-inbound-message}</MessageId>
        <AccountId>{guid-of-esendex-account-for-message}</AccountId>
        <MessageText>{Message text of inbound message}</MessageText>
        <From>{phone number of sender of the message}</From>
        <To>{phone number of the recipient of the inbound message (the
        virtual number of the esendex account in use)}</To>
      </InboundMessage>
      """
      #Create the new sms in activities
      self.activate(activity='SQLQueue', priority=1).SMSTool_pushNewSMS(
                              message_id=xml['MessageId'],
                              sender=self._parsePhoneNumber(xml['From']),
                              recipient=self._parsePhoneNumber(xml['To']),
                              text_content=xml['MessageText'],
                              message_type='text/plain',
                              reception_date=DateTime(),
                              mode="push")

    security.declareProtected(Permissions.ManagePortal, 'notifyDelivery')
    def notifyDelivery(self, xml):
      """Handle delivery info
        xml: lxml Element"""
      """
      <MessageDelivered>
        <Id>{guid-of-push-notification}</Id>
        <MessageId>{guid-of-inbound-message}</MessageId>
        <AccountId>{guid-of-esendex-account-for-message}</AccountId>
        <OccurredAt>{the UTC DateTime (yyyy-MM-ddThh:mm:ss) that the
        message was delivered to the recipient}</OccurredAt>
      </MessageDelivered>

      """

      #Convert date to DateTime
      xml['OccurredAt'] = DateTime(xml['OccurredAt'][0:19])

      self.activate(activity='SQLQueue').SMSTool_setMessageDelivery(
                            portal_type="Short Message",
                            destination_reference=xml['MessageId'],
                            delivery_date=xml['OccurredAt'])

    def pullLastMessageList(self, start_date=None, stop_date=None):
      """Get last messsages on the gateway"""

      if start_date is not None or stop_date is not None:
        base_url = self.api_url + "/GetInboxMessage.aspx"
      else:
        base_url = self.api_url + "/GetLatestInboxMessages.aspx"

      params = {'Username': self.getGatewayUser(),
                'Password': self.getGatewayPassword(),
                'Account': self.getGatewayAccount(),
                'PlainText': 1,
                }
      if start_date is not None:
        params['StartDate'] = start_date.strftime('%d/%m/%Y %H:%M:%S')

      if stop_date is not None:
        params['EndDate'] = stop_date.strftime('%d/%m/%Y %H:%M:%S')

      if self.isSimulationMode():
        params['Test'] = 1
        LOG("EssendexGateway", INFO, params)

      params = urllib.urlencode(params)
      page = urllib.urlopen(base_url, params)
      result = self._fetchPageAsDict(page)

      if result['Result'] == "OK":
        #Push all message
        type_mapping = {'Text': 'text/plain'}
        now = DateTime()
        for key, value in result.items():
          if type(key) == int:
            reception_date = self._parseDate(value['ReceivedAt'])
            #Take only message received more than 10s
            if self._convertTimeDeltaToSeconds(now - reception_date) > 10:
              self.activate(activity='SQLQueue',priority=2).SMSTool_pushNewSMS(
                                message_id=value['ID'],
                                sender=self._parsePhoneNumber(value['Originator']),
                                recipient=self._parsePhoneNumber(value['Recipient']),
                                text_content=value['Body'],
                                message_type=type_mapping[value['Type']],
                                reception_date=reception_date,
                                mode="pull")
      elif result['Result'] == "Test":
        LOG("EssendexGateway", INFO, result)
      elif result['Result'] == "Error":
        #we get an error when call the gateway
        raise SMSGatewayError, urllib.unquote(result.get('Message', "Impossible to get last message list"))


