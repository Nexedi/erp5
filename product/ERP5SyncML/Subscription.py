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

from Globals import PersistentMapping
from time import gmtime,strftime # for anchors
from SyncCode import SyncCode
from Products.CMFCore.utils import getToolByName
from Acquisition import Implicit, aq_base
from zLOG import LOG

import md5

class Conflict(SyncCode, Implicit):
  """
    object_path : the path of the obect
    keyword : an identifier of the conflict
    local_value : the value that we have locally
    remote_value : the value sent by the remote box

  """
  def __init__(self, object_path=None, keyword=None, xupdate=None, local_value=None,\
               remote_value=None, domain=None, domain_id=None):
    self.object_path=object_path
    self.keyword = keyword
    self.setLocalValue(local_value)
    self.setRemoteValue(remote_value)
    self.domain = domain
    self.resetXupdate()
    self.domain_id = domain_id

  def getObjectPath(self):
    """
    get the domain
    """
    return self.object_path

  def getLocalValue(self):
    """
    get the domain
    """
    return self.local_value

  def getXupdateList(self):
    """
    get the xupdate wich gave an error
    """
    xupdate_list = []
    if len(self.xupdate)>0:
      for xupdate in self.xupdate:
        xupdate_list+= [xupdate]
    return xupdate_list

  def resetXupdate(self):
    """
    Reset the xupdate list
    """
    self.xupdate = PersistentMapping()

  def setXupdate(self, xupdate):
    """
    set the xupdate
    """
    if xupdate == None:
      self.resetXupdate()
    else:
      self.xupdate = self.getXupdateList() + [xupdate]

  def setXupdateList(self, xupdate):
    """
    set the xupdate
    """
    self.xupdate = xupdate

  def setLocalValue(self, value):
    """
    get the domain
    """
    try:
      self.local_value = value
    except TypeError: # It happens when we try to store StringIO
      self.local_value = None

  def getRemoteValue(self):
    """
    get the domain
    """
    return self.remote_value

  def setRemoteValue(self, value):
    """
    get the domain
    """
    try:
      self.remote_value = value
    except TypeError: # It happens when we try to store StringIO
      self.remote_value = None

  def applyLocalValue(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    p_sync.applyLocalValue(self)

  def applyRemoteValue(self):
    """
    get the domain
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    p_sync.applyRemoteValue(self)

  def setDomain(self, domain):
    """
    set the domain
    """
    self.domain = domain

  def getDomain(self):
    """
    get the domain
    """
    return self.domain

  def getKeyword(self):
    """
    get the domain
    """
    return self.keyword

  def getDomainId(self):
    """
    get the domain id
    """
    return self.domain_id

  def setDomainId(self, domain_id):
    """
    set the domain
    """
    self.domain_id = domain_id

class Signature(SyncCode):
  """
    status -- SENT, CONFLICT...
    md5_object -- An MD5 value of a given document
    #uid -- The UID of the document
    id -- the ID of the document
    rid -- the uid of the document on the remote database,
        only needed on the server.
    xml -- the xml of the object at the time where it was synchronized
  """

  # Constructor
  def __init__(self,id=None, status=None, xml_string=None):
    self.id = id
    self.status = status
    self.setXML(xml_string)
    self.partial_xml = None
    self.action = None
    self.setTempXML(None)
    self.resetConflictList()
    self.md5_string = None
    self.force = 0

  #def __init__(self,object=None, status=None, xml_string=None):
  #  self.uid = object.uid
  #  self.id = object.id
  #  self.status = status
  #  self.setXML(xml_string)

  def setStatus(self, status):
    """
      set the Status (see SyncCode for numbers)
    """
    self.status = status
    if status == self.SYNCHRONIZED:
      temp_xml = self.getTempXML()
      self.setForce(0)
      if temp_xml is not None:
        # This happens when we have sent the xml
        # and we just get the confirmation
        self.setXML(self.getTempXML())
      self.setTempXML(None)
      if len(self.getConflictList())>0:
        self.resetConflictList()
    elif status in (self.PUB_CONFLICT_MERGE,self.SENT):
      # We have a solution for the conflict, don't need to keep the list
      self.resetConflictList()

  def getStatus(self):
    """
      get the Status (see SyncCode for numbers)
    """
    return self.status

  def getForce(self):
    """
      get the force value (if we need to force update or not)
    """
    return self.force

  def setForce(self, force):
    """
      set the force value (if we need to force update or not)
    """
    self.force = force

  def setXML(self, xml):
    """
      set the XML corresponding to the object
    """
    self.xml = xml
    if self.xml != None:
      self.setTempXML(None) # We make sure that the xml will not be erased
      self.setMD5(xml)

  def getXML(self):
    """
      set the XML corresponding to the object
    """
    return self.xml

  def setTempXML(self, xml):
    """
      This is the xml temporarily saved, it will
      be stored with setXML when we will receive
      the confirmation of synchronization
    """
    self.temp_xml = xml

  def getTempXML(self):
    """
      get the temp xml
    """
    return self.temp_xml

  def setMD5(self, xml):
    """
      set the MD5 object of this signature
    """
    self.md5_string = md5.new(xml).digest()

  def getMD5(self):
    """
      get the MD5 object of this signature
    """
    return self.md5_string

  def checkMD5(self, xml_string):
    """
    check if the given md5_object returns the same things as
    the one stored in this signature, this is very usefull
    if we want to know if an objects has changed or not
    Returns 1 if MD5 are equals, else it returns 0
    """
    return ((md5.new(xml_string).digest()) == self.getMD5())

  def setRid(self, rid):
    """
      set the rid
    """
    self.rid = rid

  def getRid(self):
    """
      get the rid
    """
    return self.rid

  def setId(self, id):
    """
      set the id
    """
    self.id = id

  def getId(self):
    """
      get the id
    """
    return self.id

  def setPartialXML(self, xml):
    """
    Set the partial string we will have to
    deliver in the future
    """
    #LOG('Subscriber.setPartialXML before',0,'partial_xml: %s' % str(self.partial_xml))
    self.partial_xml = xml
    #LOG('Subscriber.setPartialXML after',0,'partial_xml: %s' % str(self.partial_xml))

  def getPartialXML(self):
    """
    Set the partial string we will have to
    deliver in the future
    """
    #LOG('Subscriber.getPartialXML',0,'partial_xml: %s' % str(self.partial_xml))
    return self.partial_xml

  def getAction(self):
    """
    Return the actual action for a partial synchronization
    """
    return self.action

  def setAction(self, action):
    """
    Return the actual action for a partial synchronization
    """
    self.action = action

  def getConflictList(self):
    """
    Return the actual action for a partial synchronization
    """
    conflict_list = []
    if len(self.conflict_list)>0:
      for conflict in self.conflict_list:
        conflict_list += [conflict]
    return conflict_list

  def resetConflictList(self):
    """
    Return the actual action for a partial synchronization
    """
    self.conflict_list = PersistentMapping()

  def setConflictList(self, conflict_list):
    """
    Return the actual action for a partial synchronization
    """
    LOG('setConflictList, list',0,conflict_list)
    if conflict_list is None or conflict_list==[]:
      self.resetConflictList()
    else:
      #new_conflict_list = []
      # If two conflicts are on the same objects, then
      # we join them, so we have a conflict with many xupdate
#       for conflict in conflict_list:
#         found = None
#         for n_conflict in new_conflict_list:
#           if n_conflict.getObjectPath() == conflict.getObjectPath():
#             found = n_conflict
#         LOG('setConflictList, found',0,found)
#         if found == None:
#           new_conflict_list += [conflict]
#         else:
#           n_conflict.setXupdate(conflict.getXupdateList())
      #self.conflict_list = new_conflict_list
      self.conflict_list = conflict_list

  def delConflict(self, conflict):
    """
    Return the actual action for a partial synchronization
    """
    LOG('delConflict, conflict',0,conflict)
    conflict_list = []
    for c in self.getConflictList():
      LOG('delConflict, c==conflict',0,c==aq_base(conflict))
      if c != aq_base(conflict):
        conflict_list += [c]
    if conflict_list != []:
      self.setConflictList(conflict_list)
    else:
      self.resetConflictList()

class Subscription(SyncCode):
  """
    Subscription hold the definition of a master ODB
    from/to which a selection of objects will be synchronised

    Subscription defined by::

    publication_url -- a URI to a publication

    subsribtion_url -- URL of ourselves

    destination_path -- the place where objects are stored

    query   -- a query which defines a local set of documents which
           are going to be synchronised

    xml_mapping -- a PageTemplate to map documents to XML

    Subscription also holds private data to manage
    the synchronisation. We choose to keep an MD5 value for
    all documents which belong to the synchronisation process::

    signatures -- a dictionnary which contains the signature
           of documents at the time they were synchronized

    session_id -- it defines the id of the session
         with the server.

    last_anchor - it defines the id of the last synchronisation

    next_anchor - it defines the id of the current synchronisation

  """

  signatures = PersistentMapping()

  # Constructor
  def __init__(self, id, publication_url, subscription_url, destination_path, query, xml_mapping):
    """
      We need to create a dictionnary of
      signatures of documents which belong to the synchronisation
      process
    """
    self.id = id
    self.publication_url = (publication_url)
    self.subscription_url = str(subscription_url)
    self.destination_path = str(destination_path)
    self.query = query
    self.xml_mapping = xml_mapping
    self.anchor = None
    self.session_id = 0
    self.signatures = PersistentMapping()
    self.last_anchor = '00000000T000000Z'
    self.next_anchor = '00000000T000000Z'
    self.domain_type = self.SUB
    #self.signatures = PersitentMapping()

  # Accessors
  def getRemoteId(self, id, path=None):
    """
      Returns the remote id from a know local id
      Returns None if...
      path allows to implement recursive sync
    """
    pass

  def getSynchronizationType(self, default=None):
    """
    """
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # XXX for debugging only, to be removed
    dict_sign = {}
    for object_id in self.signatures.keys():
      dict_sign[object_id] = self.signatures[object_id].getStatus()
    LOG('getSignature',0,'signatures_status: %s' % str(dict_sign))
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    code = self.SLOW_SYNC
    if len(self.signatures.keys()) > 0:
      code = self.TWO_WAY
    if default is not None:
      code = default
    LOG('Subscription',0,'getSynchronizationType keys: %s' % str(self.signatures.keys()))
    LOG('Subscription',0,'getSynchronizationType: %s' % code)
    return code

  def getLocalId(self, rid, path=None):
    """
      Returns the local id from a know remote id
      Returns None if...
    """
    pass

  def getId(self):
    """
      return the ID
    """
    return self.id

  def setId(self, id):
    """
      set the ID
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

  def getSubscriptionUrl(self):
    """
      return the subscription url
    """
    return self.subscription_url

  def setSubscriptionUrl(self, subscription_url):
    """
      set the subscription url
    """
    self.subscription_url = subscription_url

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

  def getSubscription(self):
    """
      return the current subscription
    """
    return self

  def getSessionId(self):
    """
      return the session id
    """
    self.session_id += 1
    return self.session_id

  def getLastAnchor(self):
    """
      return the id of the last synchronisation
    """
    return self.last_anchor

  def getNextAnchor(self):
    """
      return the id of the current synchronisation
    """
    return self.next_anchor

  def setLastAnchor(self, last_anchor):
    """
      set the value last anchor
    """
    self.last_anchor = last_anchor

  def setNextAnchor(self, next_anchor):
    """
      set the value next anchor
    """
    # We store the old next anchor as the new last one
    self.last_anchor = self.next_anchor
    self.next_anchor = next_anchor

  def NewAnchor(self):
    """
      set a new anchor
    """
    self.last_anchor = self.next_anchor
    self.next_anchor = strftime("%Y%m%dT%H%M%SZ", gmtime())

  def resetAnchors(self):
    """
      reset both last and next anchors
    """
    self.last_anchor = self.NULL_ANCHOR
    self.next_anchor = self.NULL_ANCHOR

  def addSignature(self, signature):
    """
      add a Signature to the subscription
    """
    self.signatures[signature.id] = signature

  def delSignature(self, id):
    """
      add a Signature to the subscription
    """
    del self.signatures[id]

  def getSignature(self, id):
    """
      add a Signature to the subscription
    """
    # This is just a test XXX To be removed
    #dict = {}
    #for key in self.signatures.keys():
    #  dict[key]=self.signatures[key].getPartialXML()
    #LOG('Subscription',0,'dict: %s' % str(dict))
    if self.signatures.has_key(id):
      return self.signatures[id]
    return None

  def getSignatureList(self):
    """
      add a Signature to the subscription
    """
    signature_list = []
    for key in self.signatures.keys():
      signature_list += [self.signatures[key]]
    return signature_list

  def hasSignature(self, id):
    """
      Check if there's a signature with this uid
    """
    LOG('Subscription',0,'keys: %s' % str(self.signatures.keys()))
    return self.signatures.has_key(id)

  def resetAllSignatures(self):
    """
      Reset all signatures
    """
    self.signatures = PersistentMapping()

  def getIdList(self):
    """
    Returns the list of ids from signature
    """
    return self.signatures.keys()

  def getConflictList(self):
    """
    Return the list of all conflicts from all signatures
    """
    conflict_list = []
    for signature in self.getSignatureList():
      conflict_list += signature.getConflictList()
    return conflict_list

  def startSynchronization(self):
    """
    Set the status of every object as NOT_SYNCHRONIZED
    """
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # XXX for debugging only, to be removed
    dict_sign = {}
    for object_id in self.signatures.keys():
      dict_sign[object_id] = self.signatures[object_id].getStatus()
    LOG('startSynchronization',0,'signatures_status: %s' % str(dict_sign))
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    for object_id in self.signatures.keys():
      # Change the status only if we are not in a conflict mode
      if not(self.signatures[object_id].getStatus() in (self.CONFLICT,self.PUB_CONFLICT_MERGE,
                                                        self.PUB_CONFLICT_CLIENT_WIN)):
        self.signatures[object_id].setStatus(self.NOT_SYNCHRONIZED)
        self.signatures[object_id].setPartialXML(None)
        self.signatures[object_id].setTempXML(None)
