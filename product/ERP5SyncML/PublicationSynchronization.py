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
from Publication import Publication,Subscriber
from Subscription import Signature
from xml.dom.ext.reader.Sax2 import FromXmlStream, FromXml
from XMLSyncUtils import XMLSyncUtils
from Conduit.ERP5Conduit import ERP5Conduit
from Products.CMFCore.utils import getToolByName
import commands
from zLOG import LOG

class PublicationSynchronization(XMLSyncUtils):

  def PubSyncInit(self, publication=None, xml_client=None, subscriber=None, sync_type=None):
    """
      Read the client xml message
      Send the first XML message from the server
    """
    LOG('PubSyncInit',0,'Starting... publication: %s' % str(publication))

    alert = None
    # Get informations from the body
    if xml_client is not None: # We have received a message
      last_anchor = self.getAlertLastAnchor(xml_client)
      next_anchor = self.getAlertNextAnchor(xml_client)
      alert = self.checkAlert(xml_client)
      alert_code = self.getAlertCode(xml_client)

      # If slow sync, then resend everything
      if alert_code == self.SLOW_SYNC:
        LOG('Warning !!!, reseting client synchronization for subscriber:',0,subscriber)
        subscriber.resetAllSignatures()

      # Check if the last time synchronization is the same as the client one
      if subscriber.getNextAnchor() != last_anchor:
        if last_anchor == None:
          LOG('PubSyncInit',0,'anchor null')
        else:
          message = "bad anchors in PubSyncInit! " + subscriber.getNextAnchor() + \
                    " and " + last_anchor
          LOG('PubSyncInit',0,message)
      else:
        subscriber.setNextAnchor(next_anchor)

      # We have to set every object as NOT_SYNCHRONIZED
      subscriber.startSynchronization()
    else:
      # We have started the sync from the server (may be for a conflict resolution)
      pass

    xml = ""
    #if alert is not None:
    if 1:
      # Prepare the xml message for the Sync initialization package
      cmd_id = 1 # specifies a SyncML message-unique command identifier
      xml = ""
      xml += '<SyncML>\n'

      # syncml header
      xml += self.SyncMLHeader(subscriber.getSessionId(), "1",
          subscriber.getSubscriptionUrl(), publication.getPublicationUrl())

      # syncml body
      xml += ' <SyncBody>\n'
      # alert message
      xml += self.SyncMLAlert(cmd_id, sync_type, subscriber.getSubscriptionUrl(),
            publication.getPublicationUrl(), subscriber.getLastAnchor(), subscriber.getNextAnchor())
      cmd_id += 1
      xml += ' </SyncBody>\n'

      xml += '</SyncML>\n'

    self.sendResponse(from_url=publication.getPublicationUrl(),
         to_url=subscriber.getSubscriptionUrl(),sync_id=publication.id,xml=xml,
         domain=publication)
    return {'has_response':1,'xml':xml}


  def PubSync(self, id, msg=None, RESPONSE=None, subscriber=None):
    """
      This is the synchronization method for the server
    """
    LOG('PubSync',0,'Starting... id: %s' % str(id))
    # Read the request from the client
    xml_client = msg
    if xml_client is None:
      xml_client = self.readResponse(from_url='file://tmp/sync_server')
    LOG('PubSync',0,'Starting... msg: %s' % str(xml_client))
    result = None

    if xml_client is not None:
      if type(xml_client) in (type('a'),type(u'a')):
        xml_client = FromXml(xml_client)
      first_node = xml_client.childNodes[1]

      if first_node.nodeName != "SyncML":
        LOG('PubSync',0,'This is not a SyncML Message')
        return
      alert_code = self.getAlertCode(xml_client)

      # Get informations from the header
      client_header = first_node.childNodes[1]
      if client_header.nodeName != "SyncHdr":
        LOG('PubSync',0,'This is not a SyncML Header')
        return
      for subnode in client_header.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Source":
          subscription_url = str(subnode.childNodes[0].data)
      # Get the subscriber or create it if not already in the list
      subscriber = self.getPublication(id).getSubscriber(subscription_url)
      if subscriber == None:
        subscriber = Subscriber(subscription_url)
        self.getPublication(id).addSubscriber(subscriber)
        # first synchronization
        result = self.PubSyncInit(self.getPublication(id),xml_client,subscriber=subscriber,sync_type=self.SLOW_SYNC)


      elif self.checkAlert(xml_client) and alert_code in (self.TWO_WAY,self.SLOW_SYNC):
        result = self.PubSyncInit(publication=self.getPublication(id),
                         xml_client=xml_client, subscriber=subscriber,sync_type=alert_code)
      else:
        result = self.PubSyncModif(self.getPublication(id), xml_client)
    elif subscriber is not None:
      # This looks like we are starting a synchronization after
      # a conflict resolution by the user
      result = self.PubSyncInit(publication=self.getPublication(id),
                      xml_client=None, subscriber=subscriber,sync_type=self.TWO_WAY)

    has_response = 1 #pubsync always replies to messages

    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')
    elif result is not None:
      return result

  def PubSyncModif(self, publication, xml_client):
    """
    The modidification message for the publication
    """
    return self.SyncModif(publication,xml_client)
