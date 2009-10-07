# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#          Danièle Vanbaelinghem <daniele@nexedi.com>
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

from Products.ERP5Type.Globals import PersistentMapping
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
from zLOG import LOG, DEBUG, INFO

import md5
from base64 import b64encode, b64decode, b16encode, b16decode

class Signature(Folder, SyncCode):
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
  def __init__(self,
               id=None,
               rid=None,
               status=None,
               xml_string=None,
               object=None):
    if object is not None:
      self.setPath(object.getPhysicalPath())
      self.setObjectId(object.getId())
    else:
      self.setPath(None)
    self.setId(id)
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
    elif status in (self.PUB_CONFLICT_MERGE, self.SENT):
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
    return getattr(self, 'path', None)

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
    return getattr(self, 'modification_date', None)

  def setLastModificationDate(self,value):
    """
      set the last modfication date, so that we don't always
      check the xml
    """
    setattr(self, 'modification_date', value)

  def getLastSynchronizationDate(self):
    """
      get the last modfication date, so that we don't always
      check the xml
    """
    return getattr(self, 'synchronization_date', None)

  def setLastSynchronizationDate(self,value):
    """
      set the last modfication date, so that we don't always
      check the xml
    """
    setattr(self, 'synchronization_date', value)

  def setXML(self, xml):
    """
      set the XML corresponding to the object
    """
    self.xml = xml
    if self.xml is not None:
      self.setTempXML(None) # We make sure that the xml will not be erased
      self.setMD5(xml)

  def getXML(self):
    """
      get the XML corresponding to the object
    """
    #Never return empty string
    return getattr(self, 'xml', None) or None

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
    if isinstance(rid, unicode):
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
    if isinstance(id, unicode):
      id = id.encode('utf-8')
    self.id = id

  def getId(self):
    """
      get the id
    """
    return self.id

  def getGid(self):
    """
      get the gid
    """
    return self.getId()

  def setObjectId(self, id):
    """
      set the id of the object associated to this signature
    """
    if isinstance(id, unicode):
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
    self.partial_xml = xml

  def getPartialXML(self):
    """
    Set the partial string we will have to
    deliver in the future
    """
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
    returned_conflict_list = []
    if len(self.conflict_list)>0:
      returned_conflict_list.extend(self.conflict_list)
    return returned_conflict_list

  def resetConflictList(self):
    """
    Return the actual action for a partial synchronization
    """
    self.conflict_list = PersistentMapping()

  def setConflictList(self, conflict_list):
    """
    Return the actual action for a partial synchronization
    """
    if conflict_list is None or conflict_list == []:
      self.resetConflictList()
    else:
      self.conflict_list = conflict_list

  def delConflict(self, conflict):
    """
    Return the actual action for a partial synchronization
    """
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

