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
from XMLSyncUtils import XMLSyncUtils
import commands
from Conduit.ERP5Conduit import ERP5Conduit
from AccessControl import getSecurityManager
from DateTime import DateTime
from zLOG import LOG, DEBUG, INFO

class SubscriptionSynchronization(XMLSyncUtils):

  def SubSyncInit(self, subscription):
    """
      Send the first XML message from the client
    """
    #LOG('SubSyncInit',0,'starting....')
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    subscription.NewAnchor()
    subscription.initLastMessageId()

    #save the actual user to use it in all the session:
    user = getSecurityManager().getUser()
    subscription.setZopeUser(user)
    subscription.setAuthenticated(True)

    xml_list = []
    xml = xml_list.append
    xml('<SyncML>\n')
    # syncml header
    xml(self.SyncMLHeader(subscription.incrementSessionId(),
      subscription.incrementMessageId(), subscription.getPublicationUrl(),
      subscription.getSubscriptionUrl(), source_name=subscription.getLogin()))

    # syncml body
    xml(' <SyncBody>\n')

    # We have to set every object as NOT_SYNCHRONIZED
    subscription.startSynchronization()

    # alert message
    xml(self.SyncMLAlert(cmd_id, subscription.getSynchronizationType(),
                            subscription.getTargetURI(),
                            subscription.getSourceURI(),
                            subscription.getLastAnchor(),
                            subscription.getNextAnchor()))
    cmd_id += 1
    syncml_put = self.SyncMLPut(cmd_id, subscription)
    if syncml_put not in ('', None):
      xml(syncml_put)
      cmd_id += 1
    xml(' </SyncBody>\n')
    xml('</SyncML>\n')
    xml_a = ''.join(xml_list)

    self.sendResponse(from_url=subscription.subscription_url,
        to_url=subscription.publication_url, sync_id=subscription.getTitle(),
        xml=xml_a,domain=subscription,
        content_type=subscription.getSyncContentType())

    return {'has_response':1,'xml':xml_a}

  def SubSyncCred (self, subscription, msg=None, RESPONSE=None):
    """
      This method send crendentials
    """
    cmd_id = 1 # specifies a SyncML message-unique command identifier
    xml_list = []
    xml = xml_list.append
    xml('<SyncML>\n')
    # syncml header
    data = "%s:%s" % (subscription.getLogin(), subscription.getPassword())
    data=subscription.encode(subscription.getAuthenticationFormat(), data)
    xml(self.SyncMLHeader(
      subscription.incrementSessionId(),
      subscription.incrementMessageId(),
      subscription.getPublicationUrl(),
      subscription.getSubscriptionUrl(),
      source_name=subscription.getLogin(),
      dataCred=data,
      authentication_format=subscription.getAuthenticationFormat(),
      authentication_type=subscription.getAuthenticationType()))

    # syncml body
    xml(' <SyncBody>\n')

    # We have to set every object as NOT_SYNCHRONIZED
    subscription.startSynchronization()

    # alert message
    xml(self.SyncMLAlert(cmd_id, subscription.getSynchronizationType(),
                            subscription.getTargetURI(),
                            subscription.getSourceURI(),
                            subscription.getLastAnchor(),
                            subscription.getNextAnchor()))
    cmd_id += 1
    xml(self.SyncMLPut(cmd_id, subscription))
    cmd_id += 1
    xml('  <Final/>\n')
    xml(' </SyncBody>\n')
    xml('</SyncML>\n')
    xml_a = ''.join(xml_list)

    self.sendResponse(from_url=subscription.subscription_url,
        to_url=subscription.publication_url, sync_id=subscription.getTitle(),
        xml=xml_a, domain=subscription,
        content_type=subscription.getSyncContentType())

    return {'has_response':1, 'xml':xml_a}

  def SubSyncModif(self, subscription, xml_client):
    """
      Send the client modification, this happens after the Synchronization
      initialization
    """
    return self.SyncModif(subscription, xml_client)



