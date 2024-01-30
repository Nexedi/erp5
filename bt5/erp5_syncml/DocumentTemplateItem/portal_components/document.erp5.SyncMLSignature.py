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

from hashlib import md5
import six

from AccessControl import ClassSecurityInfo

from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5Type import Permissions
from Products.ERP5Type import PropertySheet
from erp5.component.module.SyncMLUtils import PdataHelper
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter


_MARKER = object()

class SyncMLSignature(XMLObject):
  """
  A Signature represent a document that is synchronized

  It contains as attribute the xml representation of the object which is used
  to generate the diff of the object between two synchronization

  It also contains the list of conflict as sub-objects when it happens
  """
  meta_type = 'ERP5 Signature'
  portal_type = 'SyncML Signature'
  isIndexable = ConstantGetter('isIndexable', value=False)

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

  security.declareProtected(Permissions.ModifyPortalContent, 'synchronize')
  def synchronize(self):
    """
    This is call when subscription get confirmation of the data synchronization
    This copy & reset some properties if needed
    """
    edit_kw = {}
    temporary_data = self.getTemporaryData()
    if temporary_data is not None:
      # This happens when we have sent the xml
      # and we just get the confirmation
      self.setData(temporary_data)
      edit_kw["temporary_data"] = None
    if self.isForce():
      edit_kw["force"] = False
    if self.hasPartialData():
      edit_kw["partial_data"] = None
    if self.hasSubscriberXupdate():
      edit_kw["subscriber_xupdate"] = None
    if self.hasPublisherXupdate():
      edit_kw["publisher_xupdate"] = None

    if len(edit_kw):
      self.edit(**edit_kw)


  security.declareProtected(Permissions.ModifyPortalContent, 'setData')
  def setData(self, value):
    """
    Set the XML corresponding to the object
    """
    if value:
      assert isinstance(value, bytes)
      # convert the bytes to Pdata
      pdata_wrapper = PdataHelper(self.getPortalObject(), value)
      self._setData(pdata_wrapper)
      self.setTemporaryData(None) # We make sure that the data will not be erased
      self.setContentMd5(pdata_wrapper.getContentMd5())
    else:
      self._setData(None)
      self.setContentMd5(None)

  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  def getData(self, default=_MARKER):
    """
    Get the XML corresponding to the object
    """
    if self.hasData():
      return bytes(self._baseGetData())
    elif default is _MARKER:
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
      self._setTemporaryData(PdataHelper(self.getPortalObject(), value))
    else:
      self._setTemporaryData(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTemporaryData')
  def getTemporaryData(self, default=_MARKER):
    """
    Return the temp xml as string
    """
    if self.hasTemporaryData():
      return bytes(self._baseGetTemporaryData())
    elif default is _MARKER:
      return self._baseGetTemporaryData()
    else:
      return self._baseGetTemporaryData(default)

  security.declareProtected(Permissions.AccessContentsInformation, 'checkMD5')
  def checkMD5(self, xml_string):
    """
    Check if the given md5_object returns the same things as the one stored in
    this signature, this is very usefull if we want to know if an objects has
    changed or not
    Returns 1 if MD5 are equals, else it returns 0
    """
    if six.PY2 and isinstance(xml_string, six.text_type):
      xml_string = xml_string.encode('utf-8')
    return md5(xml_string).hexdigest() == self.getContentMd5()

  security.declareProtected(Permissions.ModifyPortalContent, 'setPartialData')
  def setPartialData(self, value):
    """
    Set the partial string we will have to deliver in the future
    """
    if value:
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
      This is the xml temporarily saved, it will be stored with setXML when we
      will receive the confirmation of synchronization
    """
    if value:
      self._setLastData(PdataHelper(self.getPortalObject(), value))
    else:
      self._setLastData(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPartialData')
  def getPartialData(self, default=_MARKER):
    """
    Return the patial xml as string
    """
    if self.hasPartialData():
      return bytes(self._baseGetPartialData())
    elif default is _MARKER:
      return self._baseGetPartialData()
    else:
      return self._baseGetPartialData(default)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'appendPartialData')
  def appendPartialData(self, value):
    """
    Append the partial string we will have to deliver in the future
    """
    if value:
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

  security.declareProtected(Permissions.ModifyPortalContent,
                            'getFirstPdataChunk')
  def getFirstPdataChunk(self, max_len):
    """
    """
    partial_data = self._baseGetPartialData()
    chunk = partial_data[:max_len]
    rest_in_queue = partial_data[max_len:]
    if rest_in_queue is not None:
      self.setPartialData(rest_in_queue)
    return bytes(chunk)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setSubscriberXupdate')
  def setSubscriberXupdate(self, value):
    """
    This is the xml temporarily saved, it will be stored with setXML when we
    will receive the confirmation of synchronization
    """
    if value:
      self._setSubscriberXupdate(PdataHelper(self.getPortalObject(), value))
    else:
      self._setSubscriberXupdate(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSubscriberXupdate')
  def getSubscriberXupdate(self, default=_MARKER):
    """
    Return the patial xml as string
    """
    if self.hasSubscriberXupdate():
      return bytes(self._baseGetSubscriberXupdate())
    elif default is _MARKER:
      return self._baseGetSubscriberXupdate()
    else:
      return self._baseGetSubscriberXupdate(default)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'setPublisherXupdate')
  def setPublisherXupdate(self, value):
    """
    This is the xml temporarily saved, it will be stored with setXML when we
    will receive the confirmation of synchronization
    """
    if value:
      self._setPublisherXupdate(PdataHelper(self.getPortalObject(), value))
    else:
      self._setPublisherXupdate(None)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getPublisherXupdate')
  def getPublisherXupdate(self, default=_MARKER):
    """
    Return the partial xml as string
    """
    if self.hasPublisherXupdate():
      return bytes(self._baseGetPublisherXupdate())
    elif default is _MARKER:
      return self._baseGetPublisherXupdate()
    else:
      return self._baseGetPublisherXupdate(default)

  security.declareProtected(Permissions.ModifyPortalContent,
                            'getConflictList')
  def getConflictList(self):
    """
    Return the actual action for a partial synchronization
    """
    return self.contentValues()

  security.declareProtected(Permissions.ModifyPortalContent,
                            'delConflict')
  def delConflict(self, conflict):
    """
    Delete provided conflict object
    """
    self.manage_delObjects([conflict.getId(),])
