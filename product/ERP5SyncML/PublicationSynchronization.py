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
import commands
from zLOG import LOG

class PublicationSynchronization(XMLSyncUtils):

  def PubSyncInit(self, publication=None, xml_client=None, subscriber=None):
    """
      Read the client xml message
      Send the first XML message from the server
    """
    LOG('PubSyncInit',0,'Starting... publication: %s' % str(publication))

    #first_node = xml_client.childNodes[1]

    #if first_node.nodeName != "SyncML":
    #  LOG('PubSyncInit',0,'This is not a SyncML Message')

    # Get informations from the header
    #client_header = first_node.childNodes[1]
    #if client_header.nodeName != "SyncHdr":
    #  LOG('PubSyncInit',0,'This is not a SyncML Header')


    #for subnode in client_header.childNodes:
    #  if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Source":
    #    subscription_url = str(subnode.childNodes[0].data)
    #subscriber = publication.getSubscriber(subscription_url) # Get the subscriber or create it if not already in the list

    alert = None
    # Get informations from the body
    if xml_client is not None: # We have received a message
      last_anchor = self.getAlertLastAnchor(xml_client)
      next_anchor = self.getAlertNextAnchor(xml_client)
      alert = self.checkAlert(xml_client)
      alert_code = self.getAlertCode(xml_client)

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
      #file = open('/tmp/sync_init_server','w')
      cmd_id = 1 # specifies a SyncML message-unique command identifier
      xml = ""
      xml += '<SyncML>\n'

      # syncml header
      xml += self.SyncMLHeader(subscriber.getSessionId(), "1",
          subscriber.getSubscriptionUrl(), publication.getPublicationUrl())

      # syncml body
      xml += ' <SyncBody>\n'
      # alert message
      xml += self.SyncMLAlert(cmd_id, subscriber.TWO_WAY, subscriber.getSubscriptionUrl(),
            publication.getPublicationUrl(), subscriber.getLastAnchor(), subscriber.getNextAnchor())
      cmd_id += 1
      xml += ' </SyncBody>\n'

      xml += '</SyncML>\n'
      #file.write(xml)
      #file.close()

    else:
      pass

    if self.email is None:
      file = open('/tmp/sync','w')
      file.write(xml)
      file.close()
    else:
      self.sendMail(publication.publication_url, subscriber.subscription_url,
                  publication.id, xml)


  def PubSync(self, id, msg=None, RESPONSE=None, subscriber=None):
    """
      This is the synchronization method for the server
    """
    LOG('PubSync',0,'Starting... id: %s' % str(id))
    LOG('PubSync',0,'Starting... msg: %s' % str(msg))
    # Read the request from the client
    xml_client = None
    if self.email is None:
      file = open('/tmp/sync_client','r')
      xml_client = FromXmlStream(file)
      file.close()
    elif msg is not None:
      xml_client = FromXml(msg)

    if xml_client is not None:
      first_node = xml_client.childNodes[1]

      if first_node.nodeName != "SyncML":
        LOG('PubSync',0,'This is not a SyncML Message')
        return

      # Get informations from the header
      client_header = first_node.childNodes[1]
      if client_header.nodeName != "SyncHdr":
        LOG('PubSync',0,'This is not a SyncML Header')
        return
      for subnode in client_header.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and subnode.nodeName == "Source":
          subscription_url = str(subnode.childNodes[0].data)
      # Get the subscriber or create it if not already in the list
      subscriber = self.list_publications[id].getSubscriber(subscription_url)
      #file.close()
      if subscriber == None:
        subscriber = Subscriber(subscription_url)
        # FIXME: Why can't we use the method addSubscriber ??
        self.list_publications[id].addSubscriber(subscriber)
        # first synchronization
        self.PubSyncInit(self.list_publications[id],xml_client)

      elif self.checkAlert(xml_client) and self.getAlertCode(xml_client) in (self.TWO_WAY,self.SLOW_SYNC):
        self.PubSyncInit(publication=self.list_publications[id],
                         xml_client=xml_client, subscriber=subscriber)
      else:
        self.PubSyncModif(self.list_publications[id], xml_client)
    elif subscriber is not None:
      # This looks like we are starting a synchronization after
      # a conflict resolution by the user
      self.PubSyncInit(publication=self.list_publications[id],
                      xml_client=None, subscriber=subscriber)


    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  def PubSyncModif(self, publication, xml_client):
    """
    The modidification message for the publication
    """
    self.SyncModif(publication,xml_client)
