# -*- coding: utf-8 -*-
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

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Utils import deprecated
from DateTime import DateTime
from zLOG import LOG, DEBUG, INFO, WARNING
from base64 import b16encode, b16decode
from Products.ERP5SyncML.XMLSyncUtils import getConduitByName

from Products.ERP5SyncML.SyncMLConstant import MAX_OBJECTS, ACTIVITY_PRIORITY
from warnings import warn

_MARKER = []
class SyncMLSubscription(XMLObject):
  """
    Subscription hold the definition of a master ODB
    from/to which a selection of objects will be synchronized

    Subscription defined by::

    publication_url -- a URI to a publication

    subscription_url -- URL of ourselves

    destination_path -- the place where objects are stored

    query   -- a query which defines a local set of documents which
           are going to be synchronized

    xml_mapping -- a PageTemplate to map documents to XML

    gpg_key -- the name of a gpg key to use

    Subscription also holds private data to manage
    the synchronization. We choose to keep an MD5 value for
    all documents which belong to the synchronization process::

    signatures -- a dictionnary which contains the signature
           of documents at the time they were synchronized

    session_id -- it defines the id of the session
         with the server.

    last_anchor - it defines the id of the last synchronization

    next_anchor - it defines the id of the current synchronization

    Subscription inherit of File because the Signature use method _read_data
    which have the need of a __r_jar not None.
    During the initialization of a Signature this __p_jar is None 
    """

  meta_type = 'ERP5 Subscription'
  portal_type = 'SyncML Subscription' # may be useful in the future...

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference
                    , PropertySheet.Login
                    , PropertySheet.Url
                    , PropertySheet.Gpg
                    , PropertySheet.Data
                    , PropertySheet.SyncMLSubscription
                    , PropertySheet.SyncMLSubscriptionConstraint )

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isOneWayFromServer')
  def isOneWayFromServer(self):
    return self.getPortalType() == 'SyncML Subscription' and \
           self.getSyncmlAlertCode() == 'one_way_from_server'

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isOneWayFromClient')
  def isOneWayFromClient(self):
    return self.getParentValue().getPortalType() == 'SyncML Publication' and \
           self.getSyncmlAlertCode() == 'one_way_from_client'

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSynchronizationType')
  def getSynchronizationType(self, default=_MARKER):
    """Deprecated alias of getSyncmlAlertCode
    """
    warn('Use getSyncmlAlertCode instead', DeprecationWarning)
    if default is _MARKER:
      code = self.getSyncmlAlertCode()
    else:
      code = self.getSyncmlAlertCode(default=default)
    return code

  security.declarePrivate('checkCorrectRemoteSessionId')
  def checkCorrectRemoteSessionId(self, session_id):
    """
    We will see if the last session id was the same
    wich means that the same message was sent again

    return True if the session id was not seen, False if already seen
    """
    if self.getLastSessionId() == session_id:
      return False 
    self.setLastSessionId(session_id)
    return True

  security.declarePrivate('checkCorrectRemoteMessageId')
  def checkCorrectRemoteMessageId(self, message_id):
    """
    We will see if the last message id was the same
    wich means that the same message was sent again

    return True if the message id was not seen, False if already seen
    """
    if self.getLastMessageId() == message_id:
      return False
    self.setLastMessageId(message_id)
    return True 

  security.declareProtected(Permissions.ModifyPortalContent,
                            'initLastMessageId')
  def initLastMessageId(self, last_message_id=0):
    """
    set the last message id to 0
    """
    self.setLastMessageId(last_message_id)


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getXmlBindingGeneratorMethodId')
  def getXmlBindingGeneratorMethodId(self, default=_MARKER, force=False):
    """
      return the xml mapping
    """
    if self.isOneWayFromServer() and not force:
      return None
    if default is _MARKER:
      return self._baseGetXmlBindingGeneratorMethodId()
    else:
      return self._baseGetXmlBindingGeneratorMethodId(default=default)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getGidFromObject')
  def getGidFromObject(self, object, encoded=True):
    """
      Returns the object gid 
    """
    o_base = aq_base(object)
    gid = None
    # first try with new method
    gid_generator = self.getGidGeneratorMethodId("")
    if gid_generator not in ("", None) and getattr(self, gid_generator, None):
      raw_gid = getattr(self, gid_generator)(object)
    else:
      # old way using the conduit
      conduit_name = self.getConduitModuleId()
      conduit = getConduitByName(conduit_name)
      raw_gid = conduit.getGidFromObject(object)
    if isinstance(raw_gid, unicode):
      raw_gid = raw_gid.encode('ascii', 'ignore')
    if encoded:
      gid = b16encode(raw_gid)
    else:
      gid = raw_gid
    return gid

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getObjectFromGid')
  def getObjectFromGid(self, gid, use_list_method=True):
    """
    This tries to get the object with the given gid
    This uses the query if it exist and use_list_method is True
    """
    if len(gid)%2 != 0:
    #something encode in base 16 is always a even number of number
    #if not, b16decode will failed
      return None
    signature = self.getSignatureFromGid(gid)
    # First look if we do already have the mapping between
    # the id and the gid
    destination = self.getSourceValue()
    if signature is not None and signature.getReference():
      document_path = signature.getReference()
      document = self.getPortalObject().unrestrictedTraverse(document_path, None)
      if document is not None:
        return document
    #LOG('entering in the slow loop of getObjectFromGid !!!', WARNING,
        #self.getPath())
    if use_list_method:
      object_list = self.getObjectList(gid=b16decode(gid))
      for document in object_list:
        document_gid = self.getGidFromObject(document)
        if document_gid == gid:
          return document
    #LOG('getObjectFromGid', DEBUG, 'returning None')
    return None


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getObjectFromId')
  def getObjectFromId(self, id):
    """
    return the object corresponding to the id
    """
    object_list = self.getObjectList(id=id)
    o = None
    for object in object_list:
      if object.getId() == id:
        o = object
        break
    return o


  security.declareProtected(Permissions.AccessContentsInformation,
                            'getObjectList')
  def getObjectList(self, **kw):
    """
    This returns the list of sub-object corresponding
    to the query
    """
    folder = self.getSourceValue()
    list_method_id = self.getListMethodId()
    if list_method_id is not None and isinstance(list_method_id, str):
      result_list = []
      query_method = folder.unrestrictedTraverse(list_method_id, None)
      if query_method is not None:
        result_list = query_method(context_document=self, **kw)
      else:
        raise KeyError, 'This Subscriber %s provide no list method:%r'\
          % (self.getPath(), list_method_id)
    else:
      raise KeyError, 'This Subscriber %s provide no list method with id:%r'\
        % (self.getPath(), list_method_id)
    # XXX Access all objects is very costly
    return [x for x in result_list
            if not getattr(x, '_conflict_resolution', False)]


  security.declarePrivate('generateNewIdWithGenerator')
  def generateNewIdWithGenerator(self, object=None, gid=None):
    """
    This tries to generate a new Id
    """
    id_generator = self.getSynchronizationIdGeneratorMethodId()
    if id_generator is not None:
      o_base = aq_base(object)
      new_id = None
      if callable(id_generator):
        new_id = id_generator(object, gid=gid)
      elif getattr(o_base, id_generator, None) is not None:
        generator = getattr(object, id_generator)
        new_id = generator()
      else: 
        # This is probably a python script
        generator = getattr(object, id_generator)
        new_id = generator(object=object, gid=gid)
      #LOG('generateNewIdWithGenerator, new_id: ', DEBUG, new_id)
      return new_id
    return None

  security.declareProtected(Permissions.ModifyPortalContent,
                            'incrementSessionId')
  def incrementSessionId(self):
    """
      increment and return the session id
    """
    session_id = self.getSessionId()
    session_id += 1
    self._setSessionId(session_id)
    self.resetMessageId() # for a new session, the message Id must be reset
    return session_id

  security.declareProtected(Permissions.ModifyPortalContent,
                            'incrementMessageId')
  def incrementMessageId(self):
    """
      return the message id
    """
    message_id = self.getMessageId(0)
    message_id += 1
    self._setMessageId(message_id)
    return message_id

  security.declareProtected(Permissions.ModifyPortalContent,
                            'resetMessageId')
  def resetMessageId(self):
    """
      set the message id to 0
    """
    self._setMessageId(0)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'createNewAnchor')
  def createNewAnchor(self):
    """
      set a new anchor
    """
    self.setLastAnchor(self.getNextAnchor())
    self.setNextAnchor(DateTime())

  security.declareProtected(Permissions.ModifyPortalContent,
                            'resetAnchorList')
  def resetAnchorList(self):
    """
      reset both last and next anchors
    """
    self.setLastAnchor(None)
    self.setNextAnchor(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSignatureFromObjectId')
  def getSignatureFromObjectId(self, id):
    """
    return the signature corresponding to the id
    ### Use a reverse dictionary will be usefull
    to handle changes of GIDs
    """
    document = None
    # XXX very slow
    for signature in self.objectValues():
      document = signature.getSourceValue()
      if document is not None:
        if id == document.getId():
          document = signature
          break
    return document

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSignatureFromGid')
  def getSignatureFromGid(self, gid):
    """
    return the signature corresponding to the gid
    """
    return self._getOb(gid, None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getGidList')
  def getGidList(self):
    """
    Returns the list of gids from signature
    """
    return [id for id in self.getObjectIds()]

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSignatureList')
  @deprecated
  def getSignatureList(self):
    """
      Returns the list of Signatures
    """
    return self.contentValues(portal_type='SyncML Signature')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'hasSignature')
  def hasSignature(self, gid):
    """
      Check if there's a signature with this uid
    """
    return self.getSignatureFromGid(gid) is not None


  security.declareProtected(Permissions.ModifyPortalContent,
                            'resetSignatureList')
  def resetSignatureList(self):
    """
      Reset all signatures in activities
    """
    object_id_list = [id for id in self.getObjectIds()]
    object_list_len = len(object_id_list)
    for i in xrange(0, object_list_len, MAX_OBJECTS):
      current_id_list = object_id_list[i:i+MAX_OBJECTS]
      self.activate(activity='SQLQueue',
                    tag=self.getId(),
                    priority=ACTIVITY_PRIORITY).manage_delObjects(current_id_list)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getConflictList')
  def getConflictList(self, *args, **kw):
    """
    Return the list of all conflicts from all signatures
    """
    conflict_list = []
    for signature in self.objectValues():
      conflict_list.extend(signature.getConflictList())
    return conflict_list

  security.declareProtected(Permissions.ModifyPortalContent,
                            'removeRemainingObjectPath')
  def removeRemainingObjectPath(self, object_path):
    """
    We should now wich objects should still
    synchronize
    """
    remaining_object_list = self.getProperty('remaining_object_path_list')
    if remaining_object_list is None:
      # it is important to let remaining_object_path_list to None
      # it means it has not beeing initialised yet
      return
    new_list = []
    new_list.extend(remaining_object_list)
    while object_path in new_list:
      new_list.remove(object_path)
    self._edit(remaining_object_path_list=new_list)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'initialiseSynchronization')
  def initialiseSynchronization(self):
    """
    Set the status of every object as not_synchronized
    XXX Improve method to not fetch many objects in unique transaction
    """
    LOG('Subscription.initialiseSynchronization()', 0, self.getPath())
    for signature in self.contentValues(portal_type='SyncML Signature'):
      # Change the status only if we are not in a conflict mode
      if signature.getValidationState() not in ('conflict',
                              'conflict_resolved_with_merge',
                              'conflict_resolved_with_client_command_winning'):
        if self.getIsActivityEnabled():
          signature.activate(tag=self.getId(), activity='SQLQueue',
                             priority=ACTIVITY_PRIORITY).reset()
        else:
          signature.reset()
    self._edit(remaining_object_path_list=None)


