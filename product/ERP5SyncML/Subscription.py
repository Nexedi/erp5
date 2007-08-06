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
from AccessControl import ClassSecurityInfo
from Products.CMFCore.utils import getToolByName
from Acquisition import Implicit, aq_base
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Base import Base
from Products.ERP5Type import Permissions
from Products.ERP5Type import PropertySheet
from DateTime import DateTime
from zLOG import LOG

import md5

try:
    from base64 import b64encode, b64decode, b16encode, b16decode
except ImportError:
    from base64 import encodestring as b64encode, decodestring as b64decode, \
        encodestring as b16encode, decodestring as b16decode

#class Conflict(SyncCode, Implicit):
class Conflict(SyncCode, Base):
  """
    object_path : the path of the obect
    keyword : an identifier of the conflict
    publisher_value : the value that we have locally
    subscriber_value : the value sent by the remote box

  """
  isIndexable = 0
  isPortalContent = 0 # Make sure RAD generated accessors at the class level

  def __init__(self, object_path=None, keyword=None, xupdate=None, 
      publisher_value=None, subscriber_value=None, subscriber=None):
    self.object_path=object_path
    self.keyword = keyword
    self.setLocalValue(publisher_value)
    self.setRemoteValue(subscriber_value)
    self.subscriber = subscriber
    self.resetXupdate()
    self.copy_path = None

  def getObjectPath(self):
    """
    get the object path
    """
    return self.object_path

  def getPublisherValue(self):
    """
    get the domain
    """
    return self.publisher_value

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
      self.publisher_value = value
    except TypeError: # It happens when we try to store StringIO
      self.publisher_value = None

  def getSubscriberValue(self):
    """
    get the domain
    """
    return self.subscriber_value

  def setRemoteValue(self, value):
    """
    get the domain
    """
    try:
      self.subscriber_value = value
    except TypeError: # It happens when we try to store StringIO
      self.subscriber_value = None

  def applyPublisherValue(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    p_sync.applyPublisherValue(self)

  def applyPublisherDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    p_sync.applyPublisherDocument(self)

  def getPublisherDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    return p_sync.getPublisherDocument(self)

  def getPublisherDocumentPath(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    return p_sync.getPublisherDocumentPath(self)

  def getSubscriberDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    return p_sync.getSubscriberDocument(self)

  def getSubscriberDocumentPath(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    return p_sync.getSubscriberDocumentPath(self)

  def applySubscriberDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    p_sync.applySubscriberDocument(self)

  def applySubscriberValue(self,object=None):
    """
    get the domain
    """
    p_sync = getToolByName(self,'portal_synchronizations')
    p_sync.applySubscriberValue(self,object=object)

  def setSubscriber(self, subscriber):
    """
    set the domain
    """
    self.subscriber = subscriber

  def getSubscriber(self):
    """
    get the domain
    """
    return self.subscriber

  def getKeyword(self):
    """
    get the domain
    """
    return self.keyword

  def getPropertyId(self):
    """
    get the property id
    """
    return self.keyword

  def getCopyPath(self):
    """
    Get the path of the copy, or None if none has been made
    """
    copy_path = self.copy_path
    return copy_path
    
  def setCopyPath(self, path):
    """
    """
    self.copy_path = path
    

class Signature(Folder,SyncCode):
  """
    status -- SENT, CONFLICT...
    md5_object -- An MD5 value of a given document
    #uid -- The UID of the document
    id -- the ID of the document
    gid -- the global id of the document
    rid -- the uid of the document on the remote database,
        only needed on the server.
    xml -- the xml of the object at the time where it was synchronized
  """
  isIndexable = 0
  isPortalContent = 0 # Make sure RAD generated accessors at the class level
  
  # Constructor
  def __init__(self, id=None, rid=None, status=None, xml_string=None, 
      object=None):
    if object is not None:
      self.setPath(object.getPhysicalPath())
      self.setObjectId(object.getId())
    else:
      self.setPath(None)
    self.setId(id)
    self.setGid(id)
    self.setRid(rid)
    self.status = status
    self.setXML(xml_string)
    self.partial_xml = None
    self.action = None
    self.setTempXML(None)
    self.resetConflictList()
    self.md5_string = None
    self.force = 0
    self.setSubscriberXupdate(None)
    self.setPublisherXupdate(None)
    Folder.__init__(self,id)

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
        self.setXML(temp_xml)
      self.setTempXML(None)
      self.setPartialXML(None)
      self.setSubscriberXupdate(None)
      self.setPublisherXupdate(None)
      if len(self.getConflictList())>0:
        self.resetConflictList()
      # XXX This may be a problem, if the document is changed
      # during a synchronization
      self.setLastSynchronizationDate(DateTime())
      self.getParentValue().removeRemainingObjectPath(self.getPath())
    if status == self.NOT_SYNCHRONIZED:
      self.setTempXML(None)
      self.setPartialXML(None)
    elif status in (self.PUB_CONFLICT_MERGE,self.SENT):
      # We have a solution for the conflict, don't need to keep the list
      self.resetConflictList()

  def getStatus(self):
    """
      get the Status (see SyncCode for numbers)
    """
    return self.status

  def getPath(self):
    """
      get the force value (if we need to force update or not)
    """
    return getattr(self,'path',None)

  def setPath(self, path):
    """
      set the force value (if we need to force update or not)
    """
    self.path = path

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

  def getLastModificationDate(self):
    """
      get the last modfication date, so that we don't always
      check the xml
    """
    return getattr(self,'modification_date',None)

  def setLastModificationDate(self,value):
    """
      set the last modfication date, so that we don't always
      check the xml
    """
    setattr(self,'modification_date',value)

  def getLastSynchronizationDate(self):
    """
      get the last modfication date, so that we don't always
      check the xml
    """
    return getattr(self,'synchronization_date',None)

  def setLastSynchronizationDate(self,value):
    """
      set the last modfication date, so that we don't always
      check the xml
    """
    setattr(self,'synchronization_date',value)

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
      get the XML corresponding to the object
    """
    xml =  getattr(self,'xml',None)
    if xml == '':
      xml = None
    return xml

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

  def setSubscriberXupdate(self, xupdate):
    """
    set the full temp xupdate
    """
    self.subscriber_xupdate = xupdate

  def getSubscriberXupdate(self):
    """
    get the full temp xupdate
    """
    return self.subscriber_xupdate

  def setPublisherXupdate(self, xupdate):
    """
    set the full temp xupdate
    """
    self.publisher_xupdate = xupdate

  def getPublisherXupdate(self):
    """
    get the full temp xupdate
    """
    return self.publisher_xupdate

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
    if rid is type(u'a'): 
      rid = rid.encode('utf-8')
    self.rid = rid

  def getRid(self):
    """
      get the rid
    """
    return getattr(self, 'rid', None)

  def setId(self, id):
    """
      set the id
    """
    if id is type(u'a'): 
      id = id.encode('utf-8')
    self.id = id

  def getId(self):
    """
      get the id
    """
    return self.id

  def setGid(self, gid):
    """
      set the gid
    """
    if gid is type(u'a'): 
      gid = gid.encode('utf-8')
    self.gid = gid

  def getGid(self):
    """
      get the gid
    """
    return self.gid

  def setObjectId(self, id):
    """
      set the id of the object associated to this signature
    """
    if id is type(u'a'): 
      id = id.encode('utf-8')
    self.object_id = id

  def getObjectId(self):
    """
      get the id of the object associated to this signature
    """
    return getattr(self, 'object_id', None)

  def setPartialXML(self, xml):
    """
    Set the partial string we will have to
    deliver in the future
    """
    if type(xml) is type(u'a'):
      xml = xml.encode('utf-8')
    self.partial_xml = xml

  def getPartialXML(self):
    """
    Set the partial string we will have to
    deliver in the future
    """
    #LOG('Subscriber.getPartialXML',0,'partial_xml: %s' % str(self.partial_xml))
    if self.partial_xml is not None:
      self.partial_xml = self.partial_xml.replace('@-@@-@','--') # need to put back '--'
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
    # LOG('setConflictList, list',0,conflict_list)
    if conflict_list is None or conflict_list==[]:
      self.resetConflictList()
    else:
      self.conflict_list = conflict_list

  def delConflict(self, conflict):
    """
    Return the actual action for a partial synchronization
    """
    # LOG('delConflict, conflict',0,conflict)
    conflict_list = []
    for c in self.getConflictList():
      #LOG('delConflict, c==conflict',0,c==aq_base(conflict))
      if c != aq_base(conflict):
        conflict_list += [c]
    if conflict_list != []:
      self.setConflictList(conflict_list)
    else:
      self.resetConflictList()

  def getObject(self):
    """
    Returns the object corresponding to this signature
    """
    return self.getParentValue().getObjectFromGid(self.getObjectId())

  def checkSynchronizationNeeded(self, object):
    """
    We will look at date, if there is no changes, no need to syncrhonize
    """
    last_modification = DateTime(object.ModificationDate())
    # LOG('checkSynchronizationNeeded object.ModificationDate()',0,object.ModificationDate())
    last_synchronization = self.getLastSynchronizationDate()
    parent = object.aq_parent
    # XXX CPS Specific
    if parent.id == 'portal_repository': # Make sure there is no sub objects
    #if 1:
      if last_synchronization is not None and last_modification is not None \
        and self.getSubscriberXupdate() is None and self.getPublisherXupdate() is None and \
        self.getStatus()==self.NOT_SYNCHRONIZED:
        if last_synchronization > last_modification:
        #if 1:
          # LOG('checkSynchronizationNeeded, no modification on: ',0,object.id)
          self.setStatus(self.SYNCHRONIZED)
    


def addSubscription( self, id, title='', REQUEST=None ):
    """
    Add a new Subscribption
    """
    o = Subscription( id ,'','','','','','')
    self._setObject( id, o )
    if REQUEST is not None:
        return self.manage_main(self, REQUEST, update_menu=1)
    return o

#class Subscription(SyncCode, Implicit):
#class Subscription(Folder, SyncCode, Implicit, Folder, Impli):
class Subscription(Folder, SyncCode):
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

    gpg_key -- the name of a gpg key to use

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

  meta_type='ERP5 Subscription'
  portal_type='SyncML Subscription' # may be useful in the future...
  isPortalContent = 1
  isRADContent = 1
  icon = None
  isIndexable = 0
  user = None

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.SimpleItem )

  allowed_types = ( 'Signatures',)

  # Declarative constructors
  constructors =   (addSubscription,)

  # Declarative security
  security = ClassSecurityInfo()
  security.declareProtected(Permissions.ManagePortal,
                            'manage_editProperties',
                            'manage_changeProperties',
                            'manage_propertiesForm',
                              )

  # Constructor
  def __init__(self, id, title, publication_url, subscription_url, 
      destination_path, source_uri, target_uri, query, xml_mapping, 
      conduit, gpg_key, id_generator, gid_generator, media_type, login, 
      password, activity_enabled, alert_code):
    """
      We need to create a dictionnary of
      signatures of documents which belong to the synchronisation
      process
    """
    self.id = id
    self.setAlertCode(alert_code)
    self.setActivityEnabled(activity_enabled)
    self.publication_url = (publication_url)
    self.subscription_url = str(subscription_url)
    self.destination_path = str(destination_path)
    self.setSourceURI(source_uri)
    self.setTargetURI(target_uri)
    self.setQuery(query)
    self.setXMLMapping(xml_mapping)
    self.anchor = None
    self.session_id = 0
    #self.signatures = PersistentMapping()
    self.last_anchor = '00000000T000000Z'
    self.next_anchor = '00000000T000000Z'
    self.setMediaType(media_type)
    self.login = login
    self.password=password
    self.domain_type = self.SUB
    self.gpg_key = gpg_key
    self.setGidGenerator(gid_generator)
    self.setSynchronizationIdGenerator(id_generator)
    self.setConduit(conduit)
    Folder.__init__(self, id)
    self.title = title

    #self.signatures = PersitentMapping()

  def getAlertCodeList(self):
    #XXX replace by a dictionary or a list in SyncCode
    return [self.TWO_WAY, self.ONE_WAY_FROM_SERVER]

  def getAlertCode(self):
    return getattr(self, 'alert_code', 200)

  def setAlertCode(self, value):
    self.alert_code = int(value)

  def isOneWayFromServer(self):
    return self.getDomainType() == self.SUB and self.getAlertCode() == self.ONE_WAY_FROM_SERVER

  def getActivityEnabled(self):
    """
    return true if we are using activity, false otherwise
    """
    return getattr(self, 'activity_enabled', None)

  def setActivityEnabled(self, activity_enabled):
    """
    set if we are using activity or not
    """
    self.activity_enabled = activity_enabled

  def getTitle(self):
    """
    getter for title
    """
    return getattr(self,'title',None)

  def setTitle(self, value):
    """
    setter for title
    """
    self.title = value
  
  def setSourceURI(self, value):
    """
    setter for source_uri
    """
    self.source_uri = value

  def getSourceURI(self):
    """
    getter for the source_uri (the local path of the subscription)
    """
    return getattr(self, 'source_uri', None)

  def setTargetURI(self, value):
    """
    setter for target_uri
    """
    self.target_uri = value

  def getTargetURI(self):
    """
    getter for the target_uri (the distant Publication we want to synchronize 
    with)
    """
    return getattr(self, 'target_uri', None)

  def getSynchronizationType(self, default=None):
    """
    """
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    # XXX for debugging only, to be removed
    #dict_sign = {}
    #for o in self.objectValues():
      #dict_sign[o.getId()] = o.getStatus()
    # LOG('getSignature',0,'signatures_status: %s' % str(dict_sign))
    # XXXXXXXXXXXXXXXXXXXXXXXXXXXXX
    code = self.SLOW_SYNC
    if len(self.objectValues()) > 0:
      code = self.TWO_WAY
    if default is not None:
      code = default
    # LOG('Subscription',0,'getSynchronizationType: %s' % code)
    return code

  def setXMLMapping(self, value):
    """
    this the name of the method used in order to set the xml
    """
    if value == '':
      value = None
    self.xml_mapping = value

  def checkCorrectRemoteSessionId(self, session_id):
    """
    We will see if the last session id was the same
    wich means that the same message was sent again

    return True if the session id was not seen, False if already seen
    """
    last_session_id = getattr(self,'last_session_id',None)
    if last_session_id == session_id:
      return False 
    self.last_session_id = session_id
    return True

  def checkCorrectRemoteMessageId(self, message_id):
    """
    We will see if the last message id was the same
    wich means that the same message was sent again

    return True if the message id was not seen, False if already seen
    """
    last_message_id = getattr(self,'last_message_id',None)
    # LOG('checkCorrectRemoteMessageId  last_message_id =',0,last_message_id)
    # LOG('checkCorrectRemoteMessageId  message_id =',0,message_id)
    if last_message_id == message_id:
      return False
    self.last_message_id = message_id
    return True

  def initLastMessageId(self, last_message_id=0):
    """
    set the last message id to 0
    """
    self.last_message_id=last_message_id

  def getLastSentMessage(self):
    """
    This is the getter for the last message we have sent
    """
    return getattr(self,'last_sent_message','')

  def setLastSentMessage(self,xml):
    """
    This is the setter for the last message we have sent
    """
    self.last_sent_message = xml

  def getDomainType(self):
    """
      return the ID
    """
    return self.domain_type

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

  def setConduit(self, value):
    """
      set the Conduit
    """
    self.conduit = value

  def getConduit(self):
    """
      get the Conduit

    """
    return getattr(self,'conduit',None)

  def getQuery(self):
    """
      return the query
    """
    return self.query

  def getGPGKey(self):
    """
      return the gnupg key name
    """
    return getattr(self,'gpg_key','')

  def setGPGKey(self, value):
    """
      setter for the gnupg key name
    """
    self.gpg_key = value

  def setQuery(self, query):
    """
      set the query
    """
    if query == '':
      query = None
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

  def getXMLMapping(self):
    """
      return the xml mapping
    """
    xml_mapping = getattr(self,'xml_mapping','asXML')
    return xml_mapping

  def getXMLFromObject(self,object):
    """
      return the xml mapping
    """
    xml_mapping = self.getXMLMapping()
    xml = ''
    if xml_mapping is not None:
      func = getattr(object,xml_mapping,None)
      if func is not None:
        xml = func()
    return xml

  def setGidGenerator(self, method):
    """
    This set the method name wich allows to find a gid
    from any object
    """
    if method in (None,'','None'):
      method = 'getId'
    self.gid_generator = method

  def getGidGenerator(self):
    """
    This get the method name wich allows to find a gid
    from any object
    """
    return self.gid_generator

  def getMediaType(self):
    """
    This method return the type of media used in this session,
    for example, it could be "text/vcard" or "xml/text",...
    """
    return getattr(self, 'media_type', self.MEDIA_TYPE['TEXT_XML'])

  def setMediaType(self, media_type):
    """
    set the type of media used
    """
    if media_type in (None,''):
      media_type = self.MEDIA_TYPE['TEXT_XML']
    self.media_type = media_type

  def getLogin(self):
    """
    This method return the login of this subscription
    """
    return getattr(self, 'login', '')

  def setLogin(self, new_login):
    """
    set the login at new_login
    """
    self.login=new_login

  def getPassword(self):
    """
    This method return the password of this subscription
    """
    return getattr(self, 'password', '')

  def setPassword(self, new_password):
    """
    set the password at new_password
    """
    self.password=new_password
  

  def setAuthentication(self, auth):
    """
      set the value of the authentication requirement
    """
    self.auth_required = auth

  def getAuthenticationFormat(self):
    """
      return the format of authentication
    """
    return getattr(self, 'authentication_format', 'b64')

  def getAuthenticationType(self):
    """
      return the type of authentication
    """
    return getattr(self, 'authentication_type', 'syncml:auth-basic')

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

  def getGidFromObject(self, object):
    """
    """
    o_base = aq_base(object)
    o_gid = None
    gid_gen = self.getGidGenerator()
    if callable(gid_gen):
      o_gid=gid_gen(object)
    elif getattr(o_base, gid_gen, None) is not None:
      generator = getattr(object, gid_gen)
      o_gid = generator() # XXX - used to be o_gid = generator(object=object) which is redundant
    elif gid_gen is not None:
      # It might be a script python
      generator = getattr(object,gid_gen)
      o_gid = generator() # XXX - used to be o_gid = generator(object=object) which is redundant
    o_gid = b16encode(o_gid)
    return o_gid

  def getObjectFromGid(self, gid):
    """
    This tries to get the object with the given gid
    This uses the query if it exist
    """
    signature = self.getSignatureFromGid(gid)
    # First look if we do already have the mapping between
    # the id and the gid
    destination = self.getDestination()
    if signature is not None and signature.getPath() is not None:
      o = None
      try:
        o = destination.getPortalObject().restrictedTraverse(signature.getPath())
      except (AttributeError, KeyError, TypeError):
        pass
      o_id = signature.getObjectId()
      #try with id param too, because gid is not catalogged
      object_list = self.getObjectList(gid = b16decode(gid), id = o_id)
      #LOG('getObjectFromGid :',0,'object_list=%s, gid=%s, o_id=%s' % (object_list, gid, o_id))
      if o is not None and o in object_list:
        return o
    #LOG('entering in the slow loop of getObjectFromGid !!!',0,'')
    object_list = self.getObjectList(gid = b16decode(gid))
    #LOG('getObjectFromGid :', 0, 'object_list slow loop=%s, gid=%s' % (object_list, gid))
    for o in object_list:
      o_gid = self.getGidFromObject(o)
      if o_gid == gid:
        return o
    #LOG('getObjectFromGid',0,'returning None')
    return None

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

#  def setOneWaySyncFromServer(self,value):
#    """
#    If this option is enabled, then we will not 
#    send our own modifications
#    """
#    self.one_way_sync_from_server = value
#


  def getObjectList(self, **kw):
    """
    This returns the list of sub-object corresponding
    to the query
    """
    destination = self.getDestination()
    query = self.getQuery()
    query_list = []
    if query is not None and isinstance(query, str):
      query_method = getattr(destination,query,None)
      if query_method is not None:
        query_list = query_method(**kw)
    elif callable(query): # used in the test
      query_list = query(destination)
    return [x for x in query_list
              if not getattr(x,'_conflict_resolution',False)]

  def generateNewIdWithGenerator(self, object=None,gid=None):
    """
    This tries to generate a new Id
    """
    id_generator = self.getSynchronizationIdGenerator()
    if id_generator is not None:
      o_base = aq_base(object)
      new_id = None
      if callable(id_generator):
        new_id = id_generator(object,gid=gid)
      elif getattr(o_base, id_generator, None) is not None:
        generator = getattr(object, id_generator)
        new_id = generator()
      else: 
        # This is probably a python script
        generator = getattr(object, id_generator)
        new_id = generator(object=object,gid=gid)
      #LOG('generateNewId, new_id: ',0,new_id)
      return new_id
    return None

  def setSynchronizationIdGenerator(self, method):
    """
    This set the method name wich allows to generate
    a new id
    """
    if method in ('','None'):
      method = None
    self.synchronization_id_generator = method

  def getSynchronizationIdGenerator(self):
    """
    This get the method name wich allows to generate a new id
    """
    return getattr(self, 'synchronization_id_generator', None)

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

  def getDestination(self):
    """
      return the destination object itself
    """
    return self.unrestrictedTraverse(self.getDestinationPath())

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
    
  def setSessionId(self, session_id):
    """
      set the session id
    """
    self.session_id = session_id

  def getSessionId(self):
    """
      return the session id
    """
    #self.session_id += 1 #to be commented
    return self.session_id

  def incrementSessionId(self):
    """
      increment and return the session id
    """
    self.session_id += 1
    self.resetMessageId() # for a new session, the message Id must be reset
    return self.session_id

  def incrementMessageId(self):
    """
      return the message id
    """
    #self.message_id += 1
    #return self.message_id
    #return 5
    value = getattr(self, 'message_id', 0)
    self.message_id = value +1
    return self.message_id

  def getMessageId(self):
    """
      increment and return the message id
    """
    return self.message_id

  def resetMessageId(self):
    """
      set the message id to 0
    """
    self.message_id = 0
  
  def setMessageId(self, message_id):
    """
      set the message id to message_id
    """
    self.message_id = message_id

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
    if self.getSignatureFromGid(signature.getGid()) != None:
      self.delSignature(signature.getGid())
    self._setObject(signature.getGid(), aq_base(signature))

  def delSignature(self, gid):
    """
      del a Signature of the subscription
    """
    #del self.signatures[gid]
    self._delObject(gid)

  def getSignatureFromObjectId(self, id):
    """
    return the signature corresponding to the gid
    """
    o = None
    # XXX very slow
    for signature in self.getSignatureList():
      if id == signature.getObjectId():
        o = signature
        break
    return o

  def getSignatureFromGid(self, gid):
    """
    return the signature corresponding to the gid
    """
    return getattr(self, gid, None)

  def getSignatureFromRid(self, rid):
    """
    return the signature corresponding to the rid
    """
    o = None
    # XXX very slow
    for signature in self.getSignatureList():
      if rid == signature.getRid():
        o = signature
        break
    return o

  def getObjectIdList(self):
    """
    Returns the list of gids from signature
    """
    object_id_list = []
    for signature in self.getSignatureList():
      if signature.getObjectId() is not None:
        object_id_list.append(signature.getObjectId())
    return object_id_list

  def getGidList(self):
    """
    Returns the list of gids from signature
    """
    gid_list = []
    for signature in self.getSignatureList():
      if signature.getGid() is not None:
        gid_list.append(signature.getGid())
    return gid_list

  def getRidList(self):
    """
    Returns the list of rids from signature
    """
    rid_list = []
    for signature in self.getSignatureList():
      if signature.getRid() is not None:
        rid_list.append(signature.getRid())
    return rid_list

  def getSignatureList(self):
    """
      add a Signature to the subscription
    """
    return self.objectValues()

  def hasSignature(self, gid):
    """
      Check if there's a signature with this uid
    """
    #return self.signatures.has_key(gid)
    return gid in self.objectIds()

  def resetAllSignatures(self):
    """
      Reset all signatures
    """
    while len(self.objectIds())>0:
      for id in self.objectIds():
        self._delObject(id)

  def getConflictList(self):
    """
    Return the list of all conflicts from all signatures
    """
    conflict_list = []
    for signature in self.getSignatureList():
      conflict_list += signature.getConflictList()
    return conflict_list

  def getRemainingObjectPathList(self):
    """
    We should now wich objects should still
    synchronize
    """
    return getattr(self,'remaining_object_path_list',None)

  def setRemainingObjectPathList(self, value):
    """
    We should now wich objects should still
    synchronize
    """
    setattr(self,'remaining_object_path_list',value)

  def removeRemainingObjectPath(self, object_path):
    """
    We should now wich objects should still
    synchronize
    """
    remaining_object_list = self.getRemainingObjectPathList()
    if remaining_object_list is not None:
      new_list = []
      new_list.extend(remaining_object_list)
      while object_path in new_list:
        new_list.remove(object_path)
      self.setRemainingObjectPathList(new_list)

  def startSynchronization(self):
    """
    Set the status of every object as NOT_SYNCHRONIZED
    """
    for o in self.objectValues():
      # Change the status only if we are not in a conflict mode
      if not(o.getStatus() in (self.CONFLICT,self.PUB_CONFLICT_MERGE,
                                                        self.PUB_CONFLICT_CLIENT_WIN)):
        o.setStatus(self.NOT_SYNCHRONIZED)
        o.setPartialXML(None)
        o.setTempXML(None)
    self.setRemainingObjectPathList(None)


  def isAuthenticated(self):
    """
    return True if the subscriber is authenticated for this session, False 
    in other case
    """
    return self.is_authenticated
    
  def setAuthenticated(self, value):
    """
      set at True or False the value of is_authenticated is the subscriber
      is authenticated for this session or not
    """
    self.is_authenticated = value

  def encode(self, format, string_to_encode):
    """
      return the string_to_encode encoded with format format
    """
    if format in ('', None):
      return string_to_encode
    if format == 'b64':
      return b64encode(string_to_encode)
    #elif format is .... put here the other formats
    else:#if there is no format corresponding with format, raise an error
      #LOG('encode : unknown or not implemented format :', 0, format)
      raise ValueError, "Sorry, the server ask for the format %s but it's unknow or not implemented" % format

  def decode(self, format, string_to_decode):
    """
      return the string_to_decode decoded with format format
    """
    string_to_decode = string_to_decode.encode('utf-8')
    if format in ('', None):
      return string_to_decode
    if format == 'b64':
      return b64decode(string_to_decode)
    #elif format is .... put here the other formats
    else:#if there is no format corresponding with format, raise an error
      #LOG('decode : unknown or not implemented format :', 0, format)
      raise ValueError, "Sorry, the format %s is unknow or not implemented" % format

  def isDecodeEncodeTheSame(self, string_encoded, string_decoded, format):
    """
      return True if the string_encoded is equal to string_decoded encoded 
      in format
    """
    isTheSame=False
    if self.encode(format, string_decoded) == string_encoded:
      isTheSame=True
    return isTheSame


  def setUser(self, user):
    """
      save the user logged in to log him on each transaction
    """
    self.user=user

  def getUser(self):
    """
      retrun the user logged in
    """
    return self.user
