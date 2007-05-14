##############################################################################
#
# Copyright (c) 2003 Nexedi SARL and Contributors. All Rights Reserved.
#          Sebastien Robin <seb@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import smtplib # to send emails
from Subscription import Subscription,Signature
from xml.dom.ext.reader.Sax2 import FromXmlStream, FromXml
from xml.dom.minidom import parse, parseString
from xml.dom.ext import PrettyPrint
from XMLSyncUtils import XMLSyncUtils
import commands
from Conduit.ERP5Conduit import ERP5Conduit
from zLOG import LOG

class SubscriptionSynchronization(XMLSyncUtils):

  def SubSyncInit(self, subscription):
    """
      Send the first XML message from the client
    """
    LOG('SubSyncInit',0,'starting....')
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    subscription.NewAnchor()
    subscription.initLastMessageId()
    xml_list = []
    xml = xml_list.append
    xml('<SyncML>\n')
    # syncml header
    xml(self.SyncMLHeader(subscription.incrementSessionId(), 
      subscription.incrementMessageId(), subscription.getPublicationUrl(), 
      subscription.getSubscriptionUrl()))

    # syncml body
    xml(' <SyncBody>\n')

    # We have to set every object as NOT_SYNCHRONIZED
    subscription.startSynchronization()

    # alert message
    xml(self.SyncMLAlert(cmd_id, subscription.getSynchronizationType(),
                            subscription.getPublicationUrl(),
                            subscription.getDestinationPath(),
                            subscription.getLastAnchor(), 
                            subscription.getNextAnchor()))
    cmd_id += 1

    xml('  <Put>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    cmd_id += 1
    xml('  </Put>\n')
    xml(' </SyncBody>\n')
    xml('</SyncML>\n')
    xml_a = ''.join(xml_list)

    self.sendResponse(from_url=subscription.subscription_url,
        to_url=subscription.publication_url, sync_id=subscription.getTitle(), 
        xml=xml_a,domain=subscription)

    return {'has_response':1,'xml':xml_a}

  def SubSync(self, id, msg=None, RESPONSE=None):
    """
      This is the synchronization method for the client
    """
    LOG('SubSync',0,'starting... id: %s' % str(id))
    LOG('SubSync',0,'starting... msg: %s' % str(msg))
    response = None #check if subsync replies to this messages
    subscription = self.getSubscription(id)

    if msg==None and (subscription.getSubscriptionUrl()).find('file')>=0:
      msg = self.readResponse(sync_id=id, 
          from_url=subscription.getSubscriptionUrl())
    if msg==None:
      response = self.SubSyncInit(self.getSubscription(id))
    else:
      xml_client = msg
      if isinstance(xml_client, str) or isinstance(xml_client, unicode):
        xml_client = parseString(xml_client)
        next_status = self.getNextSyncBodyStatus(xml_client, None)
        #LOG('readResponse, next status :',0,next_status)
        if next_status is not None:
          status_code = self.getStatusCode(next_status)
          #LOG('readResponse status code :',0,status_code)
          if status_code == self.AUTH_REQUIRED:
            #LOG('readResponse', 0, 'Authentication required')
            response = self.SubSyncCred(id, xml_client)
          elif status_code == self.UNAUTHORIZED:
            #LOG('readResponse', 0, 'Bad authentication')
            return {'has_response':0,'xml':xml_client}
          else:
            response = self.SubSyncModif(self.getSubscription(id), xml_client)
        else: 
            response = self.SubSyncModif(self.getSubscription(id), xml_client)


    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')
    else:
      return response

  def SubSyncCred (self, id, msg=None, RESPONSE=None):
    """
      This method send crendentials
    """
    
    LOG('SubSyncCred',0,'starting... id: %s' % str(id))
    LOG('SubSyncCred',0,'starting... msg: %s' % str(msg))
    
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    subscription = self.getSubscription(id)
    xml_list = []
    xml = xml_list.append
    xml('<SyncML>\n')
    # syncml header
    data = "%s:%s" % (subscription.getLogin(), subscription.getPassword())
    data=subscription.encode(subscription.getAuthenticationFormat(), data)
    xml(self.SyncMLHeader(subscription.getSessionId(),
      subscription.incrementMessageId(), subscription.getPublicationUrl(),
      subscription.getSubscriptionUrl(), dataCred=data, 
      authentication_format=subscription.getAuthenticationFormat(), 
      authentication_type=subscription.getAuthenticationType()))

    # syncml body
    xml(' <SyncBody>\n')

    # alert message
    xml(self.SyncMLAlert(cmd_id, subscription.getSynchronizationType(),
                            subscription.getPublicationUrl(),
                            subscription.getDestinationPath(),
                            subscription.getLastAnchor(),
                            subscription.getNextAnchor()))
    cmd_id += 1

    xml('  <Put>\n')
    xml('   <CmdID>%s</CmdID>\n' % cmd_id)
    cmd_id += 1
    xml('  </Put>\n')
    xml(' </SyncBody>\n')
    xml('</SyncML>\n')
    xml_a = ''.join(xml_list)

    self.sendResponse(from_url=subscription.subscription_url,
        to_url=subscription.publication_url, sync_id=subscription.getTitle(),
        xml=xml_a,domain=subscription)

    return {'has_response':1,'xml':xml_a}

  def SubSyncModif(self, subscription, xml_client):
    """
      Send the client modification, this happens after the Synchronization
      initialization
    """
    return self.SyncModif(subscription, xml_client)



