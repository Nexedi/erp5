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
    p_sync = getToolByName(self, 'portal_synchronizations')
    p_sync.applyPublisherValue(self)

  def applyPublisherDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    p_sync.applyPublisherDocument(self)

  def getPublisherDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    return p_sync.getPublisherDocument(self)

  def getPublisherDocumentPath(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    return p_sync.getPublisherDocumentPath(self)

  def getSubscriberDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    return p_sync.getSubscriberDocument(self)

  def getSubscriberDocumentPath(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    return p_sync.getSubscriberDocumentPath(self)

  def applySubscriberDocument(self):
    """
      after a conflict resolution, we have decided
      to keep the local version of this object
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    p_sync.applySubscriberDocument(self)

  def applySubscriberValue(self, object=None):
    """
    get the domain
    """
    p_sync = getToolByName(self, 'portal_synchronizations')
    p_sync.applySubscriberValue(self, object=object)

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

