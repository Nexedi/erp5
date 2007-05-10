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
from Products.ERP5Type import Permissions
from Products.ERP5Type.Core.Folder import Folder
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import PropertySheet
from zLOG import LOG

def addSubscriber( self, id, title='', REQUEST=None ):
    """
        Add a new Category and generate UID by calling the
        ZSQLCatalog
    """
    o = Subscriber( id ,'')
    self._setObject( id, o )
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return o

class Subscriber(Subscription):
  """
    This is used to store a subscriber, with :

    subscribtion_url

    signatures -- a dictionnary which contains the signature
        of documents at the time they were synchronized.

    last_anchor - it defines the id of the last synchronisation

    next_anchor - it defines the id of the current synchronisation
  """
  def __init__(self, id, subscription_url):
    """
      constructor
    """
    self.subscription_url = subscription_url
    self.last_anchor = '00000000T000000Z'
    self.next_anchor = '00000000T000000Z'
    self.session_id = 0
    Folder.__init__(self, id)

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

  def getConduit(self):
    """
    Return the conduit of the publication
    """
    #LOG('Subscriber.getConduit, self.getPhysicalPath()',0,self.getPhysicalPath())
    #LOG('Subscriber.getConduit, self.getParent().getPhysicalPath()',0,self.aq_parent.getPhysicalPath())
    #LOG('Subscriber.getConduit, self.getParent()',0,self.getParent())
    return self.aq_parent.getConduit()
    #return self.conduit

  def SendDocuments(self):
    """
      We send all the updated documents (ie. documents not marked
      as conflicting)
    """

def addPublication( self, id, title='', REQUEST=None ):
    """
        Add a new Category and generate UID by calling the
        ZSQLCatalog
    """
    o = Publication( id ,'','','','','')
    self._setObject( id, o )
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return o

class Publication(Subscription):
  """
    Publication defined by

    publication_url

    destination_path - the place where objects are and will be stored

    query

    xml_mapping

    Contains:

    list_subscribers -- a list of subsbribtions
  """

  meta_type='ERP5 Publication'
  portal_type='SyncML Publication' # may be useful in the future...
  isPortalContent = 1
  isRADContent = 1
  icon = None

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem )

  allowed_types = ( 'Signatures',)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareProtected(Permissions.ManagePortal,
                            'manage_editProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                              )

  # Declarative constructors
  constructors =   (addPublication,)

  # Constructor
  def __init__(self, id, title, publication_url, destination_path, 
      query, xml_mapping, conduit, gpg_key, auth_required=False, 
      authentication_format='', authentication_type=''):
    """
      constructor
    """
    self.id = id
    self.publication_url = publication_url
    self.destination_path = destination_path
    self.setQuery(query)
    self.xml_mapping = xml_mapping
    #self.list_subscribers = PersistentMapping()
    self.domain_type = self.PUB
    self.gpg_key = gpg_key
    self.setGidGenerator(None)
    self.setIdGenerator(None)
    self.setConduit(conduit)
    Folder.__init__(self, id)
    self.title = title
    self.auth_required = auth_required 
    self.authentication_format = authentication_format
    self.authentication_type = authentication_type

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

  def isAuthenticationRequired(self):
    """
      return False if authentication not required, True else
    """
    return getattr(self, 'auth_required', False)

  def setAuthentication(self, auth):
    """
      set the value of the authentication requirement
    """
    self.auth_required = auth

  def getAuthenticationFormat(self):
    """
      return the format of authentication
    """
    return getattr(self, 'authentication_format', '')

  def getAuthenticationType(self):
    """
      return the type of authentication
    """
    return getattr(self, 'authentication_type', '')

  def setAuthenticationFormat(self, authentication_format):
    """
      set the format of authentication
    """
    self.authentication_format = authentication_format

  def setAuthenticationType(self, authentication_type):
    """
      set the type of authentication
    """
    self.authentication_type = authentication_type

  def addSubscriber(self, subscriber):
    """
      Add a new subscriber to the publication
    """
    # We have to remove the subscriber if it already exist (there were probably a reset on the client)
    self.delSubscriber(subscriber.getSubscriptionUrl())
    new_id = subscriber.getId()
    if new_id is None:
      new_id = str(self.generateNewId())
    subscriber.id = new_id
    #if len(self.list_subscribers) == 0:
    #  self.list_subscribers = []
    #self.list_subscribers = self.list_subscribers + [subscriber]
    self._setObject(new_id,subscriber)

  def getSubscriber(self, subscription_url):
    """
      return the subscriber corresponding the to subscription_url
    """
    for o in self.objectValues():
      if o.getSubscriptionUrl() == subscription_url:
        return o
    return None

  def getSubscriberList(self):
    """
      Get the list of subscribers
    """
    return self.objectValues()


  def delSubscriber(self, subscription_url):
    """
      Delete a subscriber for this publication
    """
    for o in self.objectValues():
      if o.getSubscriptionUrl() == subscription_url:
        self._delObject(o.id)

  def resetAllSubscribers(self):
    """
      Reset all subscribers
    """
    for o in self.objectValues():
      self._delObject(o.id)

  def getConflictList(self):
    """
      Return the list of conflicts from all subscribers
    """
    conflict_list = []
    for subscriber in self.getSubscriberList():
      conflict_list += subscriber.getConflictList()
    return conflict_list

