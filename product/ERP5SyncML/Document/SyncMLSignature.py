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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions
from Products.ERP5Type import PropertySheet

from zLOG import LOG, DEBUG, INFO
from Products.ERP5SyncML.Utils import PdataHelper
from hashlib import md5

_MARKER = []

class SyncMLSignature(XMLObject):
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
  meta_type = 'ERP5 Signature'
  portal_type = 'SyncML Signature'

  isIndexable = ConstantGetter('isIndexable', value=False)
  # Make sure RAD generated accessors at the class level

  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Reference
                    , PropertySheet.Data
                    , PropertySheet.Document
                    , PropertySheet.SyncMLSignature )

  security.declareProtected(Permissions.ModifyPortalContent, 'setData')
  def setData(self, value):
    """
      set the XML corresponding to the object
    """
    if value:
      # convert the string to Pdata
      pdata_wrapper = PdataHelper(self.getPortalObject(), value)
      #data, size = pdata_wrapper()
      self._setData(pdata_wrapper)
      self.setTemporaryData(None) # We make sure that the data will not be erased
      self.setContentMd5(pdata_wrapper.getContentMd5())
    else:
      self._setData(None)
      self.setContentMd5(None)

  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  def getData(self, default=_MARKER):
    """
      get the XML corresponding to the object
    """
    if self.hasData():
      return str(self._baseGetData())
    if default is _MARKER:
      return self._baseGetData()
    else:
      return self._baseGetData(default)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setTemporaryData')
  def setTemporaryData(self, value):
    """
      This is the xml temporarily saved, it will
      be stored with setXML when we will receive
      the confirmation of synchronization
    """
    if value:
      pdata_wrapper = PdataHelper(self.getPortalObject(), value)
      self._setTemporaryData(pdata_wrapper)
    else:
      self._setTemporaryData(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTemporaryData')
  def getTemporaryData(self, default=_MARKER):
    """
      get the temp xml
    """
    if self.hasTemporaryData():
      return str(self._baseGetTemporaryData())
    if default is _MARKER:
      return self._baseGetTemporaryData()
    else:
      return self._baseGetTemporaryData(default)

  security.declareProtected(Permissions.AccessContentsInformation, 'checkMD5')
  def checkMD5(self, xml_string):
    """
    check if the given md5_object returns the same things as
    the one stored in this signature, this is very usefull
    if we want to know if an objects has changed or not
    Returns 1 if MD5 are equals, else it returns 0
    """
    if isinstance(xml_string, unicode):
      xml_string = xml_string.encode('utf-8')
    return md5(xml_string).hexdigest() == self.getContentMd5()

  security.declareProtected(Permissions.ModifyPortalContent, 'setPartialData')
  def setPartialData(self, value):
    """
    Set the partial string we will have to
    deliver in the future
    """
    if value is not None:
      if not isinstance(value, PdataHelper):
        value = PdataHelper(self.getPortalObject(), value)
      self._setPartialData(value)
      self.setLastDataPartialData(value.getLastPdata())
    else:
      self._setPartialData(None)
      self.setLastDataPartialData(None)

  security.declareProtected(Permissions.ModifyPortalContent, 'setLastData')
  def setLastData(self, value):
    """
      This is the xml temporarily saved, it will
      be stored with setXML when we will receive
      the confirmation of synchronization
    """
    if value is not None:
      pdata_wrapper = PdataHelper(self.getPortalObject(), value)
      self._setLastData(pdata_wrapper)
    else:
      self._setLastData(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPartialData')
  def getPartialData(self, default=_MARKER):
    """
      get the patial xml
    """
    if self.hasPartialData():
      return str(self._baseGetPartialData())
    if default is _MARKER:
      return self._baseGetPartialData()
    else:
      return self._baseGetPartialData(default)

  security.declareProtected(Permissions.ModifyPortalContent, 'appendPartialData')
  def appendPartialData(self, value):
    """
    Append the partial string we will have to deliver in the future
    """
    if value is not None:
      if not isinstance(value, PdataHelper):
        value = PdataHelper(self.getPortalObject(), value)
      last_data = value.getLastPdata()
      if self.hasLastDataPartialData():
        last_data_partial_data = self.getLastDataPartialData()
        last_data_partial_data.next = value._data
        self.setLastDataPartialData(last_data_partial_data)
      else:
        self.setPartialData(value)
      self.setLastDataPartialData(last_data)

  #security.declareProtected(Permissions.AccessContentsInformation,
                            #'getFirstChunkPdata')
  #def getFirstChunkPdata(self, size_lines):
    #"""
    #"""
    #chunk = [self.getPartialData().data]
    #size = chunk[0].count('\n')

    #current = self.getPartialData()
    #next = current.next
    #while size < size_lines and next is not None:
      #current = next
      #size += current.data.count('\n')
      #chunk.append(current.data)
      #next = current.next
    #if size == size_lines:
      #self.setPartialData(next)
    #elif size > size_lines:
      #overflow = size - size_lines
      #data_list = chunk[-1].split('\n')
      #chunk[-1] = '\n'.join(data_list[:-overflow])
      #current.data = '\n'.join(data_list[-overflow:])
      #self.setPartialData(current)
    #return ''.join(chunk)

  def getFirstPdataChunk(self, max_len):
    """
    """
    #chunk, rest_in_queue = self._baseGetPartialData().\
                                             #getFirstPdataChunkAndRestInQueue(max_len)
    partial_data = self._baseGetPartialData()
    chunk = partial_data[:max_len]
    rest_in_queue = partial_data[max_len:]
    if rest_in_queue is not None:
      self.setPartialData(rest_in_queue)
    return str(chunk)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setSubscriberXupdate')
  def setSubscriberXupdate(self, value):
    """
      This is the xml temporarily saved, it will
      be stored with setXML when we will receive
      the confirmation of synchronization
    """
    if value is not None:
      pdata_wrapper = PdataHelper(self.getPortalObject(), value)
      self._setSubscriberXupdate(pdata_wrapper)
    else:
      self._setSubscriberXupdate(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberXupdate')
  def getSubscriberXupdate(self, default=_MARKER):
    """
      get the patial xml
    """
    if self.hasSubscriberXupdate():
      return str(self._baseGetSubscriberXupdate())
    if default is _MARKER:
      return self._baseGetSubscriberXupdate()
    else:
      return self._baseGetSubscriberXupdate(default)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setPublisherXupdate')
  def setPublisherXupdate(self, value):
    """
      This is the xml temporarily saved, it will
      be stored with setXML when we will receive
      the confirmation of synchronization
    """
    if value is not None:
      pdata_wrapper = PdataHelper(self.getPortalObject(), value)
      self._setPublisherXupdate(pdata_wrapper)
    else:
      self._setPublisherXupdate(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPublisherXupdate')
  def getPublisherXupdate(self, default=_MARKER):
    """
      get the patial xml
    """
    if self.hasPublisherXupdate():
      return str(self._baseGetPublisherXupdate())
    if default is _MARKER:
      return self._baseGetPublisherXupdate()
    else:
      return self._baseGetPublisherXupdate(default)


  security.declareProtected(Permissions.ModifyPortalContent,
                            'reset')
  def reset(self):
    """Clear Signature and change validation_state to not_synchronized
    """
    if self.getValidationState() != 'not_synchronized':
      self.drift()
    self.setPartialData(None)
    self.setTemporaryData(None)

  def getConflictList(self):
    """
    Return the actual action for a partial synchronization
    """
    return self.contentValues()
    # returned_conflict_list = []
    # if getattr(self, 'conflict_list', None) is None:
    #   return returned_conflict_list
    # if len(self.conflict_list)>0:
    #   returned_conflict_list.extend(self.conflict_list)
    # return returned_conflict_list

  def setConflictList(self, conflict_list):
    """
    Return the actual action for a partial synchronization
    """
    return
    # if conflict_list is None or conflict_list == []:
    #   self.resetConflictList()
    # else:
    #   self.conflict_list = conflict_list 

  def resetConflictList(self):
    """
    Return the actual action for a partial synchronization
    """
    return
    #self.conflict_list = PersistentMapping()

  def delConflict(self, conflict):
    """
    Delete provided conflict object
    """
    self.manage_delObjects([conflict.getId(),])
    # conflict_list = []
    # for c in self.getConflictList():
    #   #LOG('delConflict, c==conflict',0,c==aq_base(conflict))
    #   if c != aq_base(conflict):
    #     conflict_list += [c]
    # if conflict_list != []:
    #   self.setConflictList(conflict_list)
    # else:
    #   self.resetConflictList()

