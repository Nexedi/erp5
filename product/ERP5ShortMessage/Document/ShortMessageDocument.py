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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.Event import Event


class ShortMessageDocument(Event):
  """
    Base class for SMS. Sms are a special Event.
    They use a SMS gateway to be sended.
  """

  meta_type = 'ERP5 Short Message'
  portal_type = 'Short Message'
  isDelivery = ConstantGetter('isDelivery', value=True)

 # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.Document
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Url
                    , PropertySheet.TextDocument
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Event
                    , PropertySheet.Delivery
                    , PropertySheet.ItemAggregation
                   )

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getQuantity')
  def getQuantity(self):
    """Get quantity of sms sended"""
    #XXX-Fx : See with JPS for a new event implementation
    #XXX-Fx : DestinationReference property must be replace by a category
    return len(self.getDestinationList())

  security.declareProtected(Permissions.UseMailhostServices,
                            'isDelivered')
  def isDelivered(self):
    """Query if message is devivered or not"""
    message_quantity = self.getQuantity()
    portal = self.portal_sms

    if message_quantity == 0:
      return None

    #XXX-Fx : See with JPS for a new event implementation
    #XXX-Fx : DestinationReference property must be replace by a category
    status_list = [portal.getMessagesStatus(message_id) for message_id in self.getDestinationReference().split(',')]
    
    for status in status_list:
      if status != 'delivered':
        return False
    return True

  security.declareProtected(Permissions.UseMailhostServices, 'send')
  def send(self, from_url=None, to_url=None, reply_url=None, subject=None,
           body=None, attachment_format=None, attachment_list=None,
           download=False,**kw):
    """
      Send the current sms by using a SMS gateway.
      Use default mobile phone of source and destination
    """
    #Get the portal
    portal = self.portal_sms
    #Get recipients
    if not to_url:
      recipient_phone_list = [person.getDefaultMobileTelephoneValue() for person in self.getDestinationValueList()]
      if None in recipient_phone_list:
        raise ValueError, "All recipients should have a default mobile phone"

      to_url = [phone.asURL() for phone in recipient_phone_list]
      if None in to_url:
        raise ValueError, "All recipients should have a valid default mobile phone number"

    #Get sender
    if not from_url:
      if self.getSourceValue():
        sender_phone = self.getSourceValue().getDefaultMobileTelephoneValue()
        if not sender_phone:
          raise ValueError, "The sender should have a default mobile phone"
        #We use the title as sender
        if sender_phone.getTitle() and portal.isSendByTitleAllowed():
          from_url = sender_phone.getTitle()
        else:
          from_url = sender_phone.asURL()
      

    if not body:
      body = self.getTextContent()


    #We get the id of the message to track it
    #We only send Text message today
    message_id_list = portal.send(text=body, recipient=to_url, sender=from_url,message_type="text", test=download)

    #set message id to be able to query the status
    #XXX-Fx : See with JPS for a new event implementation
    #XXX-Fx : DestinationReference property must be replace by a category
    if message_id_list is not None:
      self.setDestinationReference(",".join(message_id_list))

    return message_id_list
