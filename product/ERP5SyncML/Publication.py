##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

from Globals import Persistent, PersistentMapping
from SyncCode import SyncCode
from Subscription import Subscription


class Subscriber(Subscription):
  """
    This is used to store a subscriber, with :

    subscribtion_url

    signatures -- a dictionnary which contains the signature
        of documents at the time they were synchronized.

    last_anchor - it defines the id of the last synchronisation

    next_anchor - it defines the id of the current synchronisation
  """
  def __init__(self, subscription_url):
    """
      constructor
    """
    self.subscription_url = subscription_url
    self.last_anchor = '00000000T000000Z'
    self.next_anchor = '00000000T000000Z'
    self.session_id = 0
    self.signatures = {}

  def ReceiveDocuments(self):
    """
      We receive documents from a subsriber
      we add if document does not exist
      we update if the local signature did not change
      we keep as conflict to be solved by user if
      local signature changed (between 2 syncs)
    """

  def ConfirmReception(self):
    """
      ?????
      Send ACK for a group of documents
    """

  def SendDocuments(self):
    """
      We send all the updated documents (ie. documents not marked
      as conflicting)
    """


class Publication(SyncCode):
  """
    Publication defined by

    publication_url

    destination_path - the place where objects are and will be stored

    query

    xml_mapping

    Contains:

    list_subscribers -- a list of subsbribtions
  """

  # Default Values
  list_subscribers = PersistentMapping()

  # Constructor
  def __init__(self, id, publication_url, destination_path, query, xml_mapping):
    """
      constructor
    """
    self.id = id
    self.publication_url = publication_url
    self.destination_path = destination_path
    self.query = query
    self.xml_mapping = xml_mapping
    self.list_subscribers = PersistentMapping()
    self.domain_type = self.PUB

  def getId(self):
    """
      return the id
    """
    return self.id

  def setId(self, id):
    """
      set the id
    """
    self.id = id

  def getQuery(self):
    """
      return the query
    """
    return self.query

  def setQuery(self, query):
    """
      set the query
    """
    self.query = query

  def getPublicationUrl(self):
    """
      return the publication url
    """
    return self.publication_url


  def getLocalUrl(self):
    """
      return the publication url
    """
    return self.publication_url

  def setPublicationUrl(self, publication_url):
    """
      return the publication url
    """
    self.publication_url = publication_url

  def getDestinationPath(self):
    """
      return the destination path
    """
    return self.destination_path

  def setDestinationPath(self, destination_path):
    """
      set the destination path
    """
    self.destination_path = destination_path

  def getXML_Mapping(self):
    """
      return the xml mapping
    """
    return self.xml_mapping

  def setXML_Mapping(self, xml_mapping):
    """
      return the xml mapping
    """
    self.xml_mapping = xml_mapping

  def addSubscriber(self, subscriber):
    """
      Add a new subscriber to the publication
    """
    # We have to remove the subscriber if it already exist (there were probably a reset on the client)
    self.delSubscriber(subscriber.getSubscriptionUrl())
    if len(self.list_subscribers) == 0:
      self.list_subscribers = []
    self.list_subscribers = self.list_subscribers + [subscriber]

  def searchSubscriber(self, subscription_url):
    """
      search if subscriber is in the list or not
    """
    for f in range(len(self.list_subscribers)):
      if self.list_subscribers[f].subscription_url == subscription_url:
        return 1
    return None

  def getSubscriber(self, subscription_url):
    """
      return the subscriber corresponding the to subscription_url
    """
    for f in range(len(self.list_subscribers)):
      if self.list_subscribers[f].subscription_url == subscription_url:
        return self.list_subscribers[f]
    return None

  def getSubscriberList(self):
    """
      Get the list of subscribers
    """
    list_subscribers = []
    for f in range(len(self.list_subscribers)):
      list_subscribers += [self.list_subscribers[f]]
    return list_subscribers

  def delSubscriber(self, subscription_url):
    """
      Delete a subscriber for this publication
    """
    for f in range(len(self.list_subscribers)):
      if self.list_subscribers[f].subscription_url == subscription_url:
        self.list_subscribers = self.list_subscribers[0:f] + self.list_subscribers[f+1:len(self.list_subscribers)]

  def resetAllSubscribers(self):
    """
      Reset all subscribers
    """
    self.list_subscribers = PersistentMapping()

  def getConflictList(self):
    """
      Return the list of conflicts from all subscribers
    """
    conflict_list = []
    for subscriber in self.getSubscriberList():
      conflict_list += subscriber.getConflictList()
    return conflict_list

