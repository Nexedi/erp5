## Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

"""\
ERP portal_synchronizations tool.
"""

from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Products.CMFCore.utils import UniqueObject
from Globals import InitializeClass, DTMLFile, PersistentMapping, Persistent
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore import CMFCorePermissions
from Products.ERP5SyncML import _dtmldir
from Publication import Publication,Subscriber
from Subscription import Subscription,Signature
from xml.dom.ext.reader.Sax2 import FromXmlStream, FromXml
from XMLSyncUtils import *
from PublicationSynchronization import PublicationSynchronization
from SubscriptionSynchronization import SubscriptionSynchronization
#import sys
#import StringIO
import string
from zLOG import *

from Conduit.ERP5Conduit import ERP5Conduit

class SynchronizationError( Exception ):
  pass

class SynchronizationTool( UniqueObject, SimpleItem,
                           SubscriptionSynchronization, PublicationSynchronization ):
  """
    This tool implements the synchronization algorithm
  """


  id       = 'portal_synchronizations'
  meta_type    = 'ERP5 Synchronizations'

  security = ClassSecurityInfo()

  #
  #  Default values.
  #
  list_publications = PersistentMapping()
  list_subscriptions = PersistentMapping()

  # Do we want to use emails ?
  #email = None
  email = 1
  same_export = 1

  def __init__( self ):
    self.list_publications = PersistentMapping()
    self.list_subscriptions = PersistentMapping()

  #
  #  ZMI methods
  #
  manage_options = ( ( { 'label'   : 'Overview'
             , 'action'   : 'manage_overview'
             }
            , { 'label'   : 'Publications'
             , 'action'   : 'managePublications'
             }
            , { 'label'   : 'Subscriptions'
             , 'action'   : 'manageSubscriptions'
             }
            , { 'label'   : 'Conflicts'
             , 'action'   : 'manageConflicts'
             }
            )
           + SimpleItem.manage_options
           )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manage_overview' )
  manage_overview = DTMLFile( 'dtml/explainSynchronizationTool', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'managePublications' )
  managePublications = DTMLFile( 'dtml/managePublications', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'addPublicationsForm' )
  addPublicationsForm = DTMLFile( 'dtml/addPublications', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manageSubsciptions' )
  manageSubscriptions = DTMLFile( 'dtml/manageSubscriptions', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manageConflicts' )
  manageConflicts = DTMLFile( 'dtml/manageConflicts', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'addSubscriptionsForm' )
  addSubscriptionsForm = DTMLFile( 'dtml/addSubscriptions', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'editProperties' )
  def editProperties( self
           , publisher=None
           , REQUEST=None
           ):
    """
      Form handler for "tool-wide" properties (including list of
      metadata elements).
    """
    if publisher is not None:
      self.publisher = publisher

    if REQUEST is not None:
      REQUEST[ 'RESPONSE' ].redirect( self.absolute_url()
                    + '/propertiesForm'
                    + '?manage_tabs_message=Tool+updated.'
                    )

  def addPublications(self, id, publication_url, destination_path,
            query, xml_mapping, RESPONSE=None):
    """
      create a new publication
    """
    pub = Publication(id, publication_url, destination_path,
                      query, xml_mapping)
    if len(self.list_publications) == 0:
      self.list_publications = PersistentMapping()
    self.list_publications[id] = pub
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  def addSubscriptions(self, id, publication_url, subscription_url,
                       destination_path, query, xml_mapping, RESPONSE=None):
    """
      create a new subscription
    """
    sub = Subscription(id, publication_url, subscription_url,
                       destination_path, query, xml_mapping)
    if len(self.list_subscriptions) == 0:
      self.list_subscriptions = PersistentMapping()
    self.list_subscriptions[id] = sub
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  def editPublications(self, id, publication_url, destination_path,
                       query, xml_mapping, RESPONSE=None):
    """
      modify a publication
    """
    pub = Publication(id, publication_url, destination_path,
                      query, xml_mapping)
    self.list_publications[id] = pub
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  def editSubscriptions(self, id, publication_url, subscription_url,
             destination_path, query, xml_mapping, RESPONSE=None):
    """
      modify a subscription
    """
    sub = Subscription(id, publication_url, subscription_url,
                       destination_path, query, xml_mapping)
    self.list_subscriptions[id] = sub
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  def deletePublications(self, id, RESPONSE=None):
    """
      delete a publication
    """
    del self.list_publications[id]
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  def deleteSubscriptions(self, id, RESPONSE=None):
    """
      delete a subscription
    """
    del self.list_subscriptions[id]
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  def ResetPublications(self, id, RESPONSE=None):
    """
      reset a publication
    """
    self.list_publications[id].resetAllSubscribers()
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  def ResetSubscriptions(self, id, RESPONSE=None):
    """
      reset a subscription
    """
    self.list_subscriptions[id].resetAllSignatures()
    self.list_subscriptions[id].resetAnchors()
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  def getPublicationList(self):
    """
      Return a list of publications
    """
    return_list = []
    if type(self.list_publications) is type([]): # For compatibility with old
                                                 # SynchronizationTool, XXX To be removed
      self.list_publications = PersistentMapping()
    for key in self.list_publications.keys():
      return_list += [self.list_publications[key]]
    return return_list

  def getSubscriptionList(self):
    """
      Return a list of publications
    """
    return_list = []
    if type(self.list_subscriptions) is type([]): # For compatibility with old
                                                 # SynchronizationTool, XXX To be removed
      self.list_subscriptions = PersistentMapping()
    for key in self.list_subscriptions.keys():
      return_list += [self.list_subscriptions[key]]
    return return_list

  def getConflictList(self):
    """
    Retrieve the list of all conflicts
    Here the list is as follow :
    [conflict_1,conflict2,...] where conflict_1 is like:
    ['publication',publication_id,object.getPath(),keyword,local_value,remote_value]
    """
    conflict_list = []
    for publication in self.getPublicationList():
      pub_conflict_list = publication.getConflictList()
      for conflict in pub_conflict_list:
        conflict.setDomain('Publication')
        conflict.setDomainId(publication.getId())
        conflict_list += [conflict]
    for subscription in self.getSubscriptionList():
      sub_conflict_list = subscription.getConflictList()
      for conflict in sub_conflict_list:
        conflict.setDomain('Subscription')
        conflict.setDomainId(subscription.getId())
        conflict_list += [conflict]
    return conflict_list

  def manageLocalValue(self, domain, domain_id, object_path, RESPONSE=None):
    """
    Do whatever needed in order to store the local value on
    the remote server
    """
    # Retrieve the conflict object
    conflict=None
    if type(object_path) is type(''):
      object_path = tuple(object_path.split('/'))
    for item in self.getConflictList():
      if item.getDomain() == domain and item.getDomainId()==domain_id \
         and item.getObjectPath()==object_path:
        conflict=item
        break
    publication = subscriber = None
    if conflict.getDomain()=='Publication': # may be we do not need the case 'subscription'
      for publication_item in self.getPublicationList():
        if conflict in publication_item.getConflictList():
          publication = publication_item
          for subscriber_item in publication.getSubscriberList():
            if conflict in subscriber_item.getConflictList():
              subscriber = subscriber_item
      if subscriber is not None and publication is not None:
        # Retrieve the signature and change the status
        publication_path = tuple(publication.getDestinationPath().split('/'))
        # Get 167 in /nexedi/server/167/default_message
        signature_id = object_path[len(publication_path)]
        signature = subscriber.getSignature(signature_id)
        signature.setStatus(signature.PUB_CONFLICT_MERGE)
        # Then launch the synchronization (wich will only be upate for conflict
        self.PubSync(publication.getId(),subscriber=subscriber)
    if RESPONSE is not None:
      RESPONSE.redirect('manageConflicts')


  def manageRemoteValue(self, domain, domain_id, object_path, RESPONSE=None):
    """
    Do whatever needed in order to store the remote value locally
    and confirmed that the remote box should keep it's value
    """
    conflict=None
    if type(object_path) is type(''):
      object_path = tuple(object_path.split('/'))
    for item in self.getConflictList():
      if item.getDomain() == domain and item.getDomainId()==domain_id \
         and item.getObjectPath()==object_path:
        conflict=item
        break
    publication = subscriber = None
    if conflict.getDomain()=='Publication': # may be we do not need the case 'subscription'
      for publication_item in self.getPublicationList():
        if conflict in publication_item.getConflictList():
          publication = publication_item
          for subscriber_item in publication.getSubscriberList():
            if conflict in subscriber_item.getConflictList():
              subscriber = subscriber_item
      if subscriber is not None and publication is not None:
        # Retrieve the signature and change the status
        publication_path = tuple(publication.getDestinationPath().split('/'))
        # Get 167 in /nexedi/server/167/default_message
        signature_id = object_path[len(publication_path)]
        signature = subscriber.getSignature(signature_id)
        signature.setStatus(signature.PUB_CONFLICT_CLIENT_WIN)
        # Then launch the synchronization (wich will only be upate for conflict
        self.PubSync(publication.getId(),subscriber=subscriber)
    if RESPONSE is not None:
      RESPONSE.redirect('manageConflicts')

InitializeClass( SynchronizationTool )
