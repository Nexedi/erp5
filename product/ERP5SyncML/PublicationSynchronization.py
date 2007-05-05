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
from xml.dom.minidom import parse, parseString
from XMLSyncUtils import XMLSyncUtils
from Conduit.ERP5Conduit import ERP5Conduit
from Products.CMFCore.utils import getToolByName
import commands
from zLOG import LOG

class PublicationSynchronization(XMLSyncUtils):
  """
    
  """

  def PubSyncInit(self, publication=None, xml_client=None, subscriber=None, 
      sync_type=None, auth_required=0):
    """
      Read the client xml message
      Send the first XML message from the server
    """
    LOG('PubSyncInit',0,'Starting... publication: %s' % str(publication))
   
    #the session id is set at the same value of those of the client
    subscriber.setSessionId(self.getSessionId(xml_client))
    # for a new session, the message Id must be reset
    subscriber.resetMessageId()     
    #the last_message_id is 1 because the message that 
    #we are about to send is the message 1      
    subscriber.initLastMessageId(1)

    alert = None
    # Get informations from the body
    if xml_client is not None: # We have received a message
      last_anchor = self.getAlertLastAnchor(xml_client)
      next_anchor = self.getAlertNextAnchor(xml_client)
      alert = self.checkAlert(xml_client)
      alert_code = self.getAlertCode(xml_client)
      cred = self.checkCred(xml_client)
      #XXX this is in developement, it's just for tests
      if not cred and auth_required:
        LOG('PubSyncInit',0,'authentication required')
	      # Prepare the xml message for the Sync initialization package
        cmd_id = 1 # specifies a SyncML message-unique command identifier
        xml_list = []
        xml = xml_list.append
        xml('<SyncML>\n')
        # syncml header
        xml(self.SyncMLHeader(subscriber.getSessionId(),
          subscriber.incrementMessageId(), subscriber.getSubscriptionUrl(), 
          publication.getPublicationUrl()))
        # syncml body
        xml(' <SyncBody>\n')
	      # chal message
        xml(self.SyncMLChal(cmd_id, "SyncHdr", publication.getPublicationUrl(), 
          subscriber.getSubscriptionUrl(), "b64", "syncml:auth-basic", 
          self.UNAUTHORIZED))
        cmd_id += 1

        xml(' </SyncBody>\n')

        xml('</SyncML>\n')
        xml_a = ''.join(xml_list)

        self.sendResponse(from_url=publication.getPublicationUrl(),
          to_url=subscriber.getSubscriptionUrl(),sync_id=publication.getTitle(),
          xml=xml_a,domain=publication)
      else :
        # If slow sync, then resend everything
        if alert_code == self.SLOW_SYNC:
          LOG('Warning !!!, reseting client synchronization for subscriber:',0,
              subscriber)
          subscriber.resetAllSignatures()

        # Check if the last time synchronization is the same as the client one
        mess='\nsubscriber.getNextAnchor:\t%s\nsubscriber.getLastAnchor:\t%s\
        \nlast_anchor:\t\t\t%s\nnext_anchor:\t\t\t%s' % (subscriber.getNextAnchor(), 
        subscriber.getLastAnchor(), last_anchor, next_anchor)
        LOG('PubSyncInit',0,mess)
        
        if subscriber.getNextAnchor() != last_anchor:
          if last_anchor == None:
            LOG('PubSyncInit',0,'anchor null')
            raise ValueError, "Sorry, the anchor was null"
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

    if alert is not None and auth_required==0:
    #if 1:
      # Prepare the xml message for the Sync initialization package
      cmd_id = 1 # specifies a SyncML message-unique command identifier
      xml_list = []
      xml = xml_list.append

      xml('<SyncML>\n')
      # syncml header
      xml(self.SyncMLHeader(subscriber.getSessionId(), 
        subscriber.incrementMessageId(), subscriber.getSubscriptionUrl(), 
        publication.getPublicationUrl()))
      # syncml body
      xml(' <SyncBody>\n')
      # alert message
      xml(self.SyncMLAlert(cmd_id, sync_type, subscriber.getSubscriptionUrl(),
        publication.getPublicationUrl(), subscriber.getLastAnchor(), 
        subscriber.getNextAnchor()))
      cmd_id += 1
      xml(' </SyncBody>\n')
      xml('</SyncML>\n')
      xml_a = ''.join(xml_list)

      self.sendResponse(from_url=publication.getPublicationUrl(),
        to_url=subscriber.getSubscriptionUrl(), sync_id=publication.getTitle(), 
        xml=xml_a, domain=publication)
    return {'has_response':1,'xml':xml_a}


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
    publication = self.getPublication(id)

    if xml_client is not None:
      if isinstance(xml_client, str) or isinstance(xml_client, unicode):
        xml_client = parseString(xml_client)
      first_node = xml_client.childNodes[0]

      if first_node.nodeName != "SyncML":
        LOG('PubSync',0,'This is not a SyncML Message')
        raise ValueError, "Sorry, This is not a SyncML Message"
      alert_code = self.getAlertCode(xml_client)

      # Get informations from the header
      client_header = first_node.childNodes[1]
      if client_header.nodeName != "SyncHdr":
        LOG('PubSync',0,'This is not a SyncML Header')
        raise ValueError, "Sorry, This is not a SyncML Header"
      for subnode in client_header.childNodes:
        if subnode.nodeType == subnode.ELEMENT_NODE and \
            subnode.nodeName == "Source":
          for subnode2 in subnode.childNodes:
            if subnode2.nodeType == subnode2.ELEMENT_NODE and \
                subnode2.nodeName == "LocURI":
              subscription_url = str(subnode2.childNodes[0].data)
      # Get the subscriber or create it if not already in the list
      subscriber = publication.getSubscriber(subscription_url)
      if subscriber == None:
        subscriber = Subscriber(publication.generateNewId(),subscription_url)
        subscriber.setXMLMapping(publication.getXMLMapping())
        publication.addSubscriber(subscriber)
        # first synchronization
        result = self.PubSyncInit(publication,xml_client,subscriber=subscriber,
            sync_type=self.SLOW_SYNC)


      elif self.checkAlert(xml_client) and \
          alert_code in (self.TWO_WAY,self.SLOW_SYNC):
        result = self.PubSyncInit(publication=publication, 
            xml_client=xml_client, subscriber=subscriber, sync_type=alert_code)
      else:
        result = self.PubSyncModif(publication, xml_client)
    elif subscriber is not None:
      # This looks like we are starting a synchronization after
      # a conflict resolution by the user
      result = self.PubSyncInit(publication=publication, xml_client=None, 
          subscriber=subscriber,sync_type=self.TWO_WAY)

    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')
    elif result is not None:
      return result

  def PubSyncModif(self, publication, xml_client):
    """
    The modidification message for the publication
    """
    return self.SyncModif(publication,xml_client)
