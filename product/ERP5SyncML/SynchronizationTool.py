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

"""
ERP portal_synchronizations tool.
"""

from OFS.SimpleItem import SimpleItem
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Base import Base
from Products.CMFCore.utils import UniqueObject
from Products.ERP5Type.Globals import InitializeClass, DTMLFile, PersistentMapping, Persistent
from AccessControl import ClassSecurityInfo, getSecurityManager
from Products.CMFCore import CMFCorePermissions
from Products.ERP5SyncML import _dtmldir
from Products.ERP5SyncML import Conduit
from Publication import Publication, Subscriber
from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2
from Subscription import Subscription
from Products.ERP5Type import Permissions
from PublicationSynchronization import PublicationSynchronization
from SubscriptionSynchronization import SubscriptionSynchronization
from SyncCode import SyncCode
from Products.CMFCore.utils import getToolByName
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.User import UnrestrictedUser
from Acquisition import aq_base
import urllib
import urllib2
import httplib
import socket
import os
import string
import commands
import random
from DateTime import DateTime
from zLOG import LOG, TRACE, DEBUG, INFO

from lxml import etree
parser = etree.XMLParser(remove_blank_text=True)

class TimeoutHTTPConnection(httplib.HTTPConnection):
  """
  Custom Classes to set timeOut on handle sockets
  """
  def connect(self):
    httplib.HTTPConnection.connect(self)
    self.sock.settimeout(3600)

class TimeoutHTTPHandler(urllib2.HTTPHandler):
  def http_open(self, req):
    return self.do_open(TimeoutHTTPConnection, req)



class SynchronizationTool( SubscriptionSynchronization,
    PublicationSynchronization, UniqueObject, Folder):
  """
    This tool implements the synchronization algorithm

    TODO: XXX-Please use BaseTool
  """


  id           = 'portal_synchronizations'
  meta_type    = 'ERP5 Synchronizations'
  portal_type  = 'Synchronisation Tool'

  # On the server, this is use to keep track of the temporary
  # copies.
  objectsToRemove = []

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

  # Multiple inheritance inconsistency caused by Base must be circumvented
  def __init__( self, *args, **kwargs ):
    Folder.__init__(self, self.id, **kwargs)


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
           + Folder.manage_options
           )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manage_overview' )
  manage_overview = DTMLFile( 'dtml/explainSynchronizationTool', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'managePublications' )
  managePublications = DTMLFile( 'dtml/managePublications', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manage_addPublicationForm' )
  manage_addPublicationForm = DTMLFile( 'dtml/manage_addPublication', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manageSubscriptions' )
  manageSubscriptions = DTMLFile( 'dtml/manageSubscriptions', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manageConflicts' )
  manageConflicts = DTMLFile( 'dtml/manageConflicts', globals() )

  security.declareProtected( CMFCorePermissions.ManagePortal
               , 'manage_addSubscriptionForm' )
  manage_addSubscriptionForm = DTMLFile( 'dtml/manage_addSubscription', globals() )

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

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_addPublication')
  def manage_addPublication(self, title, publication_url,
            destination_path, source_uri, query, xml_mapping,
            conduit, gpg_key,
            synchronization_id_generator=None, 
            media_type=None, authentication_format='b64',
            authentication_type='syncml:auth-basic',
            RESPONSE=None, activity_enabled = False,
            sync_content_type='application/vnd.syncml+xml',
            synchronize_with_erp5_sites=True):
    """
      create a new publication
    """
    folder = self.getObjectContainer()
    new_id = self.getPublicationIdFromTitle(title)
    pub = Publication(new_id, title, publication_url,
                      destination_path, source_uri, query, xml_mapping,
                      conduit, gpg_key, synchronization_id_generator,
                      media_type, 
                      authentication_format, 
                      authentication_type,
                      activity_enabled, synchronize_with_erp5_sites,
                      sync_content_type)
    folder._setObject( new_id, pub )
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_addSubscription')
  def manage_addSubscription(self, title, publication_url, subscription_url,
                       destination_path, source_uri, target_uri, query,
                       xml_mapping, conduit, gpg_key,
                       synchronization_id_generator=None,
                       media_type=None, login=None, password=None,
                       RESPONSE=None, activity_enabled=False,
                       alert_code=SyncCode.TWO_WAY,
                       synchronize_with_erp5_sites = True,
                       sync_content_type='application/vnd.syncml+xml'):
    """
      XXX should be renamed as addSubscription
      create a new subscription
    """
    folder = self.getObjectContainer()
    new_id = self.getSubscriptionIdFromTitle(title)
    sub = Subscription(new_id, title, publication_url, subscription_url,
                       destination_path, source_uri, target_uri, query,
                       xml_mapping, conduit, gpg_key,
                       synchronization_id_generator, media_type,
                       login, password, activity_enabled, alert_code,
                       synchronize_with_erp5_sites, sync_content_type)
    folder._setObject( new_id, sub )
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_editPublication')
  def manage_editPublication(self, title, publication_url,
                            destination_path, source_uri, query, xml_mapping,
                            conduit, gpg_key, synchronization_id_generator,
                            media_type=None,
                            authentication_format='b64',
                            authentication_type='syncml:auth-basic',
                            RESPONSE=None, activity_enabled=False,
                            sync_content_type='application/vnd.syncml+xml',
                            synchronize_with_erp5_sites=False):
    """
      modify a publication
    """
    pub = self.getPublication(title)
    pub.setTitle(title)
    pub.setActivityEnabled(activity_enabled)
    pub.setPublicationUrl(publication_url)
    pub.setDestinationPath(destination_path)
    pub.setSourceURI(source_uri)
    pub.setQuery(query)
    pub.setConduit(conduit)
    pub.setXMLMapping(xml_mapping)
    pub.setGPGKey(gpg_key)
    pub.setSynchronizationIdGenerator(synchronization_id_generator)
    pub.setMediaType(media_type)
    pub.setAuthenticationFormat(authentication_format)
    pub.setAuthenticationType(authentication_type)
    pub.setSyncContentType(sync_content_type)
    pub.setSynchronizeWithERP5Sites(synchronize_with_erp5_sites)

    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  security.declareProtected(Permissions.ModifyPortalContent, 
      'manage_editSubscription')
  def manage_editSubscription(self, title, publication_url, subscription_url,
      destination_path, source_uri, target_uri, query, xml_mapping, conduit,
      gpg_key, synchronization_id_generator, media_type=None,
      login='', password='', RESPONSE=None, activity_enabled=False,
      alert_code=SyncCode.TWO_WAY, synchronize_with_erp5_sites=False,
      sync_content_type='application/vnd.syncml+xml'):
    """
      modify a subscription
    """
    sub = self.getSubscription(title)
    sub.setTitle(title)
    sub.setActivityEnabled(activity_enabled)
    sub.setPublicationUrl(publication_url)
    sub.setDestinationPath(destination_path)
    sub.setSourceURI(source_uri)
    sub.setTargetURI(target_uri)
    sub.setQuery(query)
    sub.setConduit(conduit)
    sub.setXMLMapping(xml_mapping)
    sub.setGPGKey(gpg_key)
    sub.setSubscriptionUrl(subscription_url)
    sub.setSynchronizationIdGenerator(synchronization_id_generator)
    sub.setMediaType(media_type)
    sub.setLogin(login)
    sub.setPassword(password)
    sub.setSyncContentType(sync_content_type)
    sub.setSynchronizeWithERP5Sites(synchronize_with_erp5_sites)
    sub.setAlertCode(alert_code)

    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_deletePublication')
  def manage_deletePublication(self, title, RESPONSE=None):
    """
      delete a publication
    """
    id = self.getPublicationIdFromTitle(title)
    folder = self.getObjectContainer()
    folder._delObject(id)
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_deleteSubscription')
  def manage_deleteSubscription(self, title, RESPONSE=None):
    """
      delete a subscription
    """
    id = self.getSubscriptionIdFromTitle(title)
    folder = self.getObjectContainer()
    folder._delObject(id)
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_resetPublication')
  def manage_resetPublication(self, title, RESPONSE=None):
    """
      reset a publication
    """
    pub = self.getPublication(title)
    pub.resetAllSubscribers()
    if RESPONSE is not None:
      RESPONSE.redirect('managePublications')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_resetSubscription')
  def manage_resetSubscription(self, title, RESPONSE=None):
    """
      reset a subscription
    """
    sub = self.getSubscription(title)
    sub.resetAllSignatures()
    sub.resetAnchors()
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manage_syncSubscription')
  def manage_syncSubscription(self, title, RESPONSE=None):
    """
      reset a subscription
    """
    self.SubSync(self.getSubscription(title).getPath())
    if RESPONSE is not None:
      RESPONSE.redirect('manageSubscriptions')

  security.declareProtected(Permissions.AccessContentsInformation,
      'getPublicationList')
  def getPublicationList(self):
    """
      Return a list of publications
    """
    folder = self.getObjectContainer()
    return [pub for pub in folder.objectValues() if pub.getDomainType() == self.PUB]

  security.declareProtected(Permissions.AccessContentsInformation,
      'getPublication')
  def getPublication(self, title):
    """
      Return the  publications with this id
    """
    pub = None
    for p in self.getPublicationList():
      if p.getTitle() == title:
        pub = p
        break
    return pub

  security.declareProtected(Permissions.AccessContentsInformation,
      'getObjectContainer')
  def getObjectContainer(self):
    """
    this returns the external mount point if there is one
    """
    folder = self
    portal_url = getToolByName(self,'portal_url')
    root = portal_url.getPortalObject().aq_parent
    if 'external_mount_point' in root.objectIds():
      folder = root.external_mount_point
    return folder

  security.declareProtected(Permissions.AccessContentsInformation,
      'getSubscriptionList')
  def getSubscriptionList(self):
    """
      Return a list of publications
    """
    folder = self.getObjectContainer()
    return [sub for sub in folder.objectValues() if sub.getDomainType() == self.SUB]

  def getSubscription(self, title):
    """
      Returns the subscription with this title
    """
    sub = None
    for s in self.getSubscriptionList():
      if s.getTitle() == title:
        sub = s
    return sub


  security.declareProtected(Permissions.AccessContentsInformation,
      'getSynchronizationList')
  def getSynchronizationList(self):
    """
      Returns the list of subscriptions and publications
    """
    return self.getSubscriptionList() + self.getPublicationList()

  security.declareProtected(Permissions.AccessContentsInformation,
      'getSubscriberList')
  def getSubscriberList(self):
    """
      Returns the list of subscribers and subscriptions
    """
    s_list = []
    s_list.extend(self.getSubscriptionList())
    for publication in self.getPublicationList():
      s_list.extend(publication.getSubscriberList())
    return s_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getConflictList')
  def getConflictList(self, context=None):
    """
    Retrieve the list of all conflicts
    Here the list is as follow :
    [conflict_1,conflict2,...] where conflict_1 is like:
    ['publication',publication_id,object.getPath(),property_id,
    publisher_value,subscriber_value]
    """
    path = self.resolveContext(context)
    conflict_list = []
    for publication in self.getPublicationList():
      for subscriber in publication.getSubscriberList():
        sub_conflict_list = subscriber.getConflictList()
        for conflict in sub_conflict_list:
          conflict.setSubscriber(subscriber)
          if path is None or conflict.getObjectPath() == path:
            conflict_list += [conflict.__of__(subscriber)]
    for subscription in self.getSubscriptionList():
      sub_conflict_list = subscription.getConflictList()
      #LOG('SynchronizationTool.getConflictList, sub_conflict_list', DEBUG,
          #sub_conflict_list)
      for conflict in sub_conflict_list:
        conflict.setSubscriber(subscription)
        if path is None or conflict.getObjectPath() == path:
          conflict_list += [conflict.__of__(subscription)]
    return conflict_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getDocumentConflictList')
  def getDocumentConflictList(self, context=None):
    """
    Retrieve the list of all conflicts for a given document
    Well, this is the same thing as getConflictList with a path
    """
    return self.getConflictList(context)


  security.declareProtected(Permissions.AccessContentsInformation,
      'getSynchronizationState')
  def getSynchronizationState(self, context):
    """
    context : the context on which we are looking for state

    This functions have to retrieve the synchronization state,
    it will first look in the conflict list, if nothing is found,
    then we have to check on a publication/subscription.

    This method returns a mapping between subscription and states

    JPS suggestion:
      path -> object, document, context, etc.
      type -> '/titi/toto' or ('','titi', 'toto') or <Base instance 1562567>
      object = self.resolveContext(context) (method to add)
    """
    path = self.resolveContext(context)
    conflict_list = self.getConflictList()
    state_list= []
    #LOG('getSynchronizationState', DEBUG, 'path: %s' % str(path))
    for conflict in conflict_list:
      if conflict.getObjectPath() == path:
        #LOG('getSynchronizationState', DEBUG, 'found a conflict: %s' % str(conflict))
        state_list.append([conflict.getSubscriber(), self.CONFLICT])
    for domain in self.getSynchronizationList():
      destination = domain.getDestinationPath()
      #LOG('getSynchronizationState', TRACE, 'destination: %s' % str(destination))
      j_path = '/'.join(path)
      #LOG('getSynchronizationState', TRACE, 'j_path: %s' % str(j_path))
      if j_path.find(destination)==0:
        o_id = j_path[len(destination)+1:].split('/')[0]
        #LOG('getSynchronizationState', TRACE, 'o_id: %s' % o_id)
        if domain.domain_type==self.PUB:
          subscriber_list = domain.getSubscriberList()
        else:
          subscriber_list = [domain]
        #LOG('getSynchronizationState, subscriber_list:', TRACE, subscriber_list)
        for subscriber in subscriber_list:
          signature = subscriber.getSignatureFromObjectId(o_id)
          #XXX check if signature could be not None ...
          if signature is not None:
            state = signature.getStatus()
            #LOG('getSynchronizationState:', TRACE, 'sub.dest :%s, state: %s' % \
                                   #(subscriber.getSubscriptionUrl(),str(state)))
            found = False
            # Make sure there is not already a conflict giving the state
            for state_item in state_list:
              if state_item[0] == subscriber:
                found = True
            if not found:
              state_list.append([subscriber, state])
    return state_list

  security.declareProtected(Permissions.AccessContentsInformation,
      'getAlertCodeList')
  def getAlertCodeList(self):
    return self.CODE_LIST

  security.declareProtected(Permissions.ModifyPortalContent,
      'applyPublisherValue')
  def applyPublisherValue(self, conflict):
    """
      after a conflict resolution, we have decided
      to keep the local version of an object
    """
    object = self.unrestrictedTraverse(conflict.getObjectPath())
    subscriber = conflict.getSubscriber()
    # get the signature:
    #LOG('p_sync.applyPublisherValue, subscriber: ', DEBUG, subscriber)
    signature = subscriber.getSignatureFromObjectId(object.getId()) # XXX may be change for rid
    copy_path = conflict.getCopyPath()
    signature.delConflict(conflict)
    if len(signature.getConflictList()) == 0:
      if copy_path is not None:
        #LOG('p_sync.applyPublisherValue, conflict_list empty on : ', TRACE, signature)
        # Delete the copy of the object if the there is one
        directory = object.aq_parent
        copy_id = copy_path[-1]
        #LOG('p_sync.applyPublisherValue, copy_id: ', TRACE, copy_id)
        if hasattr(directory.aq_base, 'hasObject'):
          # optimize the case of a BTree folder
          #LOG('p_sync.applyPublisherValue, deleting...: ', TRACE, copy_id)
          if directory.hasObject(copy_id):
            directory._delObject(copy_id)
        elif copy_id in directory.objectIds():
          directory._delObject(copy_id)
      signature.setStatus(self.PUB_CONFLICT_MERGE)

  security.declareProtected(Permissions.ModifyPortalContent,
      'applyPublisherDocument')
  def applyPublisherDocument(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    subscriber = conflict.getSubscriber()
    for c in self.getConflictList(conflict.getObjectPath()):
      if c.getSubscriber() == subscriber:
        #LOG('applyPublisherDocument, applying on conflict: ', DEBUG, conflict)
        c.applyPublisherValue()

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getPublisherDocumentPath')
  def getPublisherDocumentPath(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    subscriber = conflict.getSubscriber()
    return conflict.getObjectPath()

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getPublisherDocument')
  def getPublisherDocument(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    publisher_object_path = self.getPublisherDocumentPath(conflict)
    #LOG('getPublisherDocument publisher_object_path', TRACE, publisher_object_path)
    publisher_object = self.unrestrictedTraverse(publisher_object_path)
    return publisher_object


  def getSubscriberDocumentVersion(self, conflict, docid):
    """
    Given a 'conflict' and a 'docid' refering to a new version of a
    document, applies the conflicting changes to the document's new
    version. By so, two differents versions of the same document will be
    available.
    Thus, the manager will be able to open both version of the document
    before selecting which one to keep.
    """
    subscriber = conflict.getSubscriber()
    publisher_object_path = conflict.getObjectPath()
    publisher_object = self.unrestrictedTraverse(publisher_object_path)
    publisher_xml = self.getXMLObject(
                              object=publisher_object,
                              xml_mapping=subscriber.getXMLMapping())
    directory = publisher_object.aq_parent
    object_id = docid
    if object_id in directory.objectIds():
        directory._delObject(object_id)
        # Import the conduit and get it
        conduit_name = subscriber.getConduit()
        conduit = self.getConduitByName(conduit_name)
        conduit.addNode(
                    xml=publisher_xml,
                    object=directory,
                    object_id=object_id)
        subscriber_document = directory._getOb(object_id)
        for c in self.getConflictList(conflict.getObjectPath()):
            if c.getSubscriber() == subscriber:
                c.applySubscriberValue(object=subscriber_document)
        return subscriber_document

  def _getCopyId(self, object):
    directory = object.aq_inner.aq_parent
    if directory.getId() != 'portal_repository':
      object_id = object.getId() + '_conflict_copy'
      if object_id in directory.objectIds():
        directory._delObject(object_id)
    else:
      repotool = directory
      docid, rev = repotool.getDocidAndRevisionFromObjectId(object.getId())
      new_rev = repotool.getFreeRevision(docid) + 10 # make sure it's not gonna provoke conflicts
      object_id = repotool._getId(docid, new_rev)
    return object_id

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getSubscriberDocumentPath')
  def getSubscriberDocumentPath(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    copy_path = conflict.getCopyPath()
    if copy_path is not None:
      return copy_path
    subscriber = conflict.getSubscriber()
    publisher_object_path = conflict.getObjectPath()
    publisher_object = self.unrestrictedTraverse(publisher_object_path)
    conduit_name = subscriber.getConduit()
    conduit = self.getConduitByName(conduit_name)
    publisher_xml = conduit.getXMLFromObjectWithId(publisher_object,\
                    xml_mapping=subscriber.getXMLMapping())
    directory = publisher_object.aq_inner.aq_parent
    object_id = self._getCopyId(publisher_object)
    # Import the conduit and get it
    conduit.addNode(
                xml=publisher_xml,
                object=directory,
                object_id=object_id)
    subscriber_document = directory._getOb(object_id)
    subscriber_document._conflict_resolution = 1
    for c in self.getConflictList(conflict.getObjectPath()):
      if c.getSubscriber() == subscriber:
        c.applySubscriberValue(object=subscriber_document)
    copy_path = subscriber_document.getPhysicalPath()
    conflict.setCopyPath(copy_path)
    return copy_path

  security.declareProtected(Permissions.AccessContentsInformation, 
      'getSubscriberDocument')
  def getSubscriberDocument(self, conflict):
    """
    apply the publisher value for all conflict of the given document
    """
    subscriber_object_path = self.getSubscriberDocumentPath(conflict)
    subscriber_object = self.unrestrictedTraverse(subscriber_object_path)
    return subscriber_object

  security.declareProtected(Permissions.ModifyPortalContent, 
      'applySubscriberDocument')
  def applySubscriberDocument(self, conflict):
    """
    apply the subscriber value for all conflict of the given document
    """
    subscriber = conflict.getSubscriber()
    for c in self.getConflictList(conflict.getObjectPath()):
      if c.getSubscriber() == subscriber:
        c.applySubscriberValue()

  security.declareProtected(Permissions.ModifyPortalContent, 
      'applySubscriberValue')
  def applySubscriberValue(self, conflict,object=None):
    """
      after a conflict resolution, we have decided
      to keep the local version of an object
    """
    solve_conflict = 1
    if object is None:
      object = self.unrestrictedTraverse(conflict.getObjectPath())
    else:
      # This means an object was given, this is used in order
      # to see change on a copy, so don't solve conflict
      solve_conflict=0
    subscriber = conflict.getSubscriber()
    # get the signature:
    signature = subscriber.getSignatureFromObjectId(object.getId()) # XXX may be change for rid
    # Import the conduit and get it
    conduit_name = subscriber.getConduit()
    conduit = self.getConduitByName(conduit_name)
    for xupdate in conflict.getXupdateList():
      conduit.updateNode(xml=xupdate, object=object, force=1)
    if solve_conflict:
      copy_path = conflict.getCopyPath()
      signature.delConflict(conflict)
      if not signature.getConflictList():
        if copy_path is not None:
          # Delete the copy of the object if the there is one
          directory = object.aq_parent
          copy_id = copy_path[-1]
          if getattr(directory.aq_base, 'hasObject', None) is not None:
            # optimize the case of a BTree folder
            if directory.hasObject(id):
              directory._delObject(copy_id)
          elif copy_id in directory.objectIds():
            directory._delObject(copy_id)
        signature.setStatus(self.PUB_CONFLICT_MERGE)

  security.declareProtected(Permissions.ModifyPortalContent,
      'managePublisherValue')
  def managePublisherValue(self, subscription_url, property_id, object_path,
      RESPONSE=None):
    """
    Do whatever needed in order to store the local value on
    the remote server

    Suggestion (API)
      add method to view document with applied xupdate
      of a given subscriber XX
      (ex. viewSubscriberDocument?path=ddd&subscriber_id=dddd)
      Version=Version CPS
    """
    # Retrieve the conflict object
    #LOG('manageLocalValue', DEBUG, '%s %s %s' % (str(subscription_url),
                                          #str(property_id),
                                          #str(object_path)))
    for conflict in self.getConflictList():
      if conflict.getPropertyId() == property_id:
        if '/'.join(conflict.getObjectPath()) == object_path:
          if conflict.getSubscriber().getSubscriptionUrl() == subscription_url:
            conflict.applyPublisherValue()
    if RESPONSE is not None:
      RESPONSE.redirect('manageConflicts')

  security.declareProtected(Permissions.ModifyPortalContent, 
      'manageSubscriberValue')
  def manageSubscriberValue(self, subscription_url, property_id, object_path, 
      RESPONSE=None):
    """
    Do whatever needed in order to store the remote value locally
    and confirmed that the remote box should keep it's value
    """
    #LOG('manageLocalValue', DEBUG, '%s %s %s' % (str(subscription_url),
                                          #str(property_id),
                                          #str(object_path)))
    for conflict in self.getConflictList():
      if conflict.getPropertyId() == property_id:
        if '/'.join(conflict.getObjectPath()) == object_path:
          if conflict.getSubscriber().getSubscriptionUrl() == subscription_url:
            conflict.applySubscriberValue()
    if RESPONSE is not None:
      RESPONSE.redirect('manageConflicts')

  security.declareProtected(Permissions.ModifyPortalContent,
      'manageSubscriberDocument')
  def manageSubscriberDocument(self, subscription_url, object_path):
    """
    """
    for conflict in self.getConflictList():
      if '/'.join(conflict.getObjectPath()) == object_path:
        if conflict.getSubscriber().getSubscriptionUrl() == subscription_url:
          conflict.applySubscriberDocument()
          break
    self.managePublisherDocument(object_path)

  security.declareProtected(Permissions.ModifyPortalContent, 
      'managePublisherDocument')
  def managePublisherDocument(self, object_path):
    """
    """
    retry = True
    while retry:
      retry = False
      for conflict in self.getConflictList():
        if '/'.join(conflict.getObjectPath()) == object_path:
          conflict.applyPublisherDocument()
          retry = True
          break

  def resolveContext(self, context):
    """
    We try to return a path (like ('','erp5','foo') from the context.
    Context can be :
      - a path
      - an object
      - a string representing a path
    """
    if context is None:
      return context
    elif isinstance(context, tuple):
      return context
    elif isinstance(context, tuple):
      return tuple(context.split('/'))
    else:
      return context.getPhysicalPath()

  security.declarePublic('sendResponse')
  def sendResponse(self, to_url=None, from_url=None, sync_id=None, xml=None,
      domain=None, send=1, content_type='application/vnd.syncml+xml'):
    """
    We will look at the url and we will see if we need to send mail, http
    response, or just copy to a file.
    """
    #LOG('sendResponse, self.getPhysicalPath: ', INFO, self.getPhysicalPath())
    #LOG('sendResponse, to_url: ', INFO, to_url)
    #LOG('sendResponse, from_url: ', INFO, from_url)
    #LOG('sendResponse, sync_id: ', INFO, sync_id)
    #LOG('sendResponse, xml: \n', INFO, xml)
    if content_type == self.CONTENT_TYPE['SYNCML_WBXML']:
      xml = self.xml2wbxml(xml)
      #LOG('sendHttpResponse, xml after wbxml: \n', DEBUG, self.hexdump(xml))
    if domain is not None:
      gpg_key = domain.getGPGKey()
      if gpg_key not in ('',None):
        filename = str(random.randrange(1,2147483600)) + '.txt'
        decrypted = file('/tmp/%s' % filename,'w')
        decrypted.write(xml)
        decrypted.close()
        (status,output)=commands.getstatusoutput('gzip /tmp/%s' % filename)
        (status,output)=commands.getstatusoutput('gpg --yes --homedir \
            /var/lib/zope/Products/ERP5SyncML/gnupg_keys -r "%s" -se \
            /tmp/%s.gz' % (gpg_key,filename))
        #LOG('readResponse, gpg output:', DEBUG, output)
        encrypted = file('/tmp/%s.gz.gpg' % filename,'r')
        xml = encrypted.read()
        encrypted.close()
        commands.getstatusoutput('rm -f /tmp/%s.gz' % filename)
        commands.getstatusoutput('rm -f /tmp/%s.gz.gpg' % filename)
    if send:
      if isinstance(to_url, str):
        if to_url.find('http://') == 0:
          domain = aq_base(domain)
          if domain.domain_type == self.PUB and not domain.getActivityEnabled():
            # not use activity
            # XXX Make sure this is not a problem
            return None
          #use activities to send send an http response
          #LOG('sendResponse, will start sendHttpResponse, xml', DEBUG, '')
          self.activate(activity='SQLQueue',
                        tag=domain.getId(),
                        priority=self.PRIORITY).sendHttpResponse(
                                              sync_id=sync_id,
                                              to_url=to_url,
                                              xml=xml,
                                              domain_path=domain.getPath(),
                                              content_type=content_type)
        elif to_url.find('file://') == 0:
          filename = to_url[len('file:/'):]
          stream = file(filename, 'w')
          stream.write(xml)
          stream.close()
          # we have to use local files (unit testing for example
        elif to_url.find('mailto:') == 0:
          # we will send an email
          to_address = to_url[len('mailto:'):]
          from_address = from_url[len('mailto:'):]
          self.sendMail(from_address, to_address, sync_id, xml)
    return xml

  security.declarePrivate('sendHttpResponse')
  def sendHttpResponse(self, to_url=None, sync_id=None, xml=None,
                       domain_path=None, content_type='application/vnd.syncml+xml'):
    domain = self.unrestrictedTraverse(domain_path)
    #LOG('sendHttpResponse, starting with domain:', DEBUG, domain)
    if domain is not None:
      if domain.domain_type == self.PUB and not domain.getActivityEnabled():
        return xml
    # Retrieve the proxy from os variables
    proxy_url = ''
    if os.environ.has_key('http_proxy'):
      proxy_url = os.environ['http_proxy']
    #LOG('sendHttpResponse, proxy_url:', DEBUG, proxy_url)
    if proxy_url !='':
      proxy_handler = urllib2.ProxyHandler({"http" :proxy_url})
    else:
      proxy_handler = urllib2.ProxyHandler({})
    pass_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    auth_handler = urllib2.HTTPBasicAuthHandler(pass_mgr)
    proxy_auth_handler = urllib2.ProxyBasicAuthHandler(pass_mgr)
    opener = urllib2.build_opener(proxy_handler, proxy_auth_handler,
        auth_handler, TimeoutHTTPHandler)
    urllib2.install_opener(opener)
    to_encode = {}
    to_encode['text'] = xml
    to_encode['sync_id'] = sync_id
    headers = {'User-Agent':'ERP5SyncML', 'Content-Type':content_type}

    #XXX bad hack for synchronization with erp5
    # because at this time, when we call the readResponse method, we must
    # encode the data with urlencode if we want the readResponse method to 
    # receive the data's in parameters.
    # All this should be improved to not use urlencode in all cases.
    # to do this, perhaps use SOAP :
    #  - http://en.wikipedia.org/wiki/SOAP
    #  - http://www.contentmanagementsoftware.info/zope/SOAPSupport
    #  - http://svn.zope.org/soap/trunk/

    if domain.getSynchronizeWithERP5Sites():
      #LOG('Synchronization with another ERP5 instance ...', DEBUG, '')
      if to_url.find('readResponse')<0:
        to_url = to_url + '/portal_synchronizations/readResponse'
      encoded = urllib.urlencode(to_encode)
      data = encoded
      request = urllib2.Request(url=to_url, data=data)
    else:
      #XXX only to synchronize with other server than erp5 (must be improved):
      data = head+xml
      request = urllib2.Request(to_url, data, headers)

    try:
      url_file = urllib2.urlopen(request)
      result = url_file.read()
    except socket.error, msg:
      self.activate(activity='SQLQueue',
                    tag=domain.getId(),
                    priority=self.PRIORITY).sendHttpResponse(
                                                  to_url=to_url,
                                                  sync_id=sync_id,
                                                  xml=xml,
                                                  domain_path=domain.getPath(),
                                                  content_type=content_type)
      LOG('sendHttpResponse, socket ERROR:', INFO, msg)
      LOG('sendHttpResponse, url, data', INFO, (to_url, data))
      return
    except urllib2.URLError, msg:
      LOG("sendHttpResponse, can't open url %s :" % to_url, INFO, msg)
      LOG('sendHttpResponse, to_url, data', INFO, (to_url, data))
      return

    if domain is not None:
      if domain.domain_type == self.SUB and not domain.getActivityEnabled():
        #if we don't use activity :
        gpg_key = domain.getGPGKey()
        if result:
          self.readResponse(sync_id=sync_id, text=result)
    return result

  security.declarePublic('sync')
  def sync(self):
    """
    This will try to synchronize every subscription
    """
    message_list = self.portal_activities.getMessageList()
    #LOG('sync, len(message_list):', DEBUG, len(message_list))
    if len(message_list) == 0:
      for subscription in self.getSubscriptionList():
        user_id = subscription.getZopeUser()
        uf = self.getPortalObject().acl_users
        user = uf.getUserById(user_id).__of__(uf)
        newSecurityManager(None, user)
        subscription.activate(activity='SQLQueue',
                              tag=subscription.getId(),
                              priority=self.PRIORITY
                                  ).SubSync(subscription.getPath())

  security.declarePublic('readResponse')
  def readResponse(self, text='', sync_id=None, to_url=None, from_url=None):
    """
    We will look at the url and we will see if we need to send mail, http
    response, or just copy to a file.
    """
    #LOG('readResponse, text :', DEBUG, text)
    #LOG('readResponse, hexdump(text) :', DEBUG, self.hexdump(text))
    status_code = None
    if text:
      # XXX We will look everywhere for a publication/subsription with
      # the id sync_id, this is not so good, but there is no way yet
      # to know if we will call a publication or subscription XXX
      gpg_key = ''
      #LOG('readResponse, sync_id :', DEBUG, sync_id)
      for publication in self.getPublicationList():
        if publication.getTitle() == sync_id:
          gpg_key = publication.getGPGKey()
          domain = publication
          break
      if not gpg_key:
        for subscription in self.getSubscriptionList():
          if subscription.getTitle() == sync_id:
            gpg_key = subscription.getGPGKey()
            domain = subscription
            user = domain.getZopeUser()
            #LOG('readResponse, user :', DEBUG, user)
            newSecurityManager(None, user)
            break
      # decrypt the message if needed
      else:
        filename = str(random.randrange(1, 2147483600)) + '.txt'
        encrypted = file('/tmp/%s.gz.gpg' % filename,'w')
        encrypted.write(text)
        encrypted.close()
        (status, output) = commands.getstatusoutput('gpg --homedir \
            /var/lib/zope/Products/ERP5SyncML/gnupg_keys -r "%s"  --decrypt \
            /tmp/%s.gz.gpg > /tmp/%s.gz' % (gpg_key, filename, filename))
        LOG('readResponse, gpg output:', TRACE, output)
        (status,output)=commands.getstatusoutput('gunzip /tmp/%s.gz' % filename)
        decrypted = file('/tmp/%s' % filename,'r')
        text = decrypted.read()
        LOG('readResponse, text:', TRACE, text)
        decrypted.close()
        commands.getstatusoutput('rm -f /tmp/%s' % filename)
        commands.getstatusoutput('rm -f /tmp/%s.gz.gpg' % filename)
      # Get the target and then find the corresponding publication or
      # Subscription
      #LOG('type(text) : ', TRACE, type(text))
      if domain.getSyncContentType() == self.CONTENT_TYPE['SYNCML_WBXML']:
        text = self.wbxml2xml(text)
      #LOG('readResponse, text after wbxml :\n', TRACE, text)
      xml = etree.XML(text, parser=parser)
      url = self.getTarget(xml)
      for publication in self.getPublicationList():
        if publication.getPublicationUrl() == url and \
        publication.getTitle() == sync_id:
          if publication.getActivityEnabled():
            #use activities to send SyncML data.
            publication.activate(activity='SQLQueue',
                                tag=publication.getId(),
                                priority=self.PRIORITY).PubSync(
                                                        publication.getPath(),
                                                        text)
            return ' '
          else:
            result = self.PubSync(publication.getPath(), xml)
            # Then encrypt the message
            xml = result['xml']
            if publication.getSyncContentType() ==\
             self.CONTENT_TYPE['SYNCML_WBXML']:
              xml = self.xml2wbxml(xml)
            return xml
      for subscription in self.getSubscriptionList():
        if subscription.getSubscriptionUrl() == url and \
            subscription.getTitle() == sync_id:
              subscription_path = subscription.getPath()
              self.activate(activity='SQLQueue',
                            tag=subscription.getId(),
                            priority=self.PRIORITY).SubSync(
                                                      subscription_path,
                                                      text)
              return ' '
    # we use from only if we have a file
    elif isinstance(from_url, str):
      if from_url.find('file://') == 0:
        try:
          filename = from_url[len('file:/'):]
          stream = file(filename, 'r')
          xml = stream.read()
          #LOG('readResponse', DEBUG, 'file... msg: %s' % str(stream.read()))
        except IOError:
          LOG('readResponse, cannot read file: ', INFO, filename)
          xml = None
        if xml is not None and len(xml) == 0:
          xml = None
        return xml

  security.declareProtected(Permissions.ModifyPortalContent, 
      'getPublicationIdFromTitle')
  def getPublicationIdFromTitle(self, title):
    """
    simply return an id from a title
    """
    return 'pub_' + title

  security.declareProtected(Permissions.ModifyPortalContent, 
      'getPublicationIdFromTitle')
  def getSubscriptionIdFromTitle(self, title):
    """
    simply return an id from a title
    """
    return 'sub_' + title

  security.declareProtected(Permissions.ModifyPortalContent, 'addNode')
  def addNode(self, conduit='ERP5Conduit', **kw):
    """
    """
    # Import the conduit and get it
    conduit_object = self.getConduitByName(conduit)
    return conduit_object.addNode(**kw)

  def hexdump(self, raw=''):
    """
    this function is used to display the raw in a readable format :
    it display raw in hexadecimal format and display too the printable 
    characters (because if not printable characters are printed, it makes 
    terminal display crash)
    """
    buf = ""
    line = ""
    start = 0
    done = False
    while not done:
      end = start + 16
      max = len(str(raw))
      if end > max:
        end = max
        done = True
      chunk = raw[start:end]
      for i in xrange(len(chunk)):
        if i > 0:
          spacing = " "
        else:
          spacing = ""
        buf += "%s%02x" % (spacing, ord(chunk[i]))
      if done:
        for i in xrange(16 - (end % 16)):
          buf += "   "
      buf += "  "
      for c in chunk:
        val = ord(c)
        if val >= 33 and val <= 126:
          buf += c
        else:
          buf += "."
      buf += "\n"
      start += 16
    return buf
InitializeClass( SynchronizationTool )
