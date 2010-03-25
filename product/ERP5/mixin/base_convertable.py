# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Jean-Paul Smets-Solanes <jp@nexedi.com>
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################

import md5
import string
import xmlrpclib, base64, re, zipfile, cStringIO
from xmlrpclib import Fault
from xmlrpclib import Transport
from xmlrpclib import SafeTransport
from Acquisition import aq_base
from AccessControl import ClassSecurityInfo
from Products.ERP5Type import Permissions
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Cache import DEFAULT_CACHE_SCOPE
from Products.ERP5Type.Base import WorkflowMethod
from zLOG import LOG
from Products.ERP5Type.Cache import CachingMethod

# Mixin import
from Products.ERP5.mixin.convertable import ConvertableMixin




class BaseConvertableMixin:
  """
  This class provides a generic implementation of IBaseConvertable.

  """

  # Declarative security
  security = ClassSecurityInfo()


  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)
  


  security.declareProtected(Permissions.AccessContentsInformation, 'hasBaseData')
  def hasBaseData(self):
    """
        A TextDocument store its data in the "text_content" property. Since
        there is no such thing as base_data in TextDocument, having base_data
        is equivalent to having some text_content.
    """
    return self.hasTextContent()

  def convertFile(self, **kw): # XXX - It it really useful to explicitly define ?
    """
    Workflow transition invoked when conversion occurs.
    """
  convertFile = WorkflowMethod(convertFile)

  security.declareProtected(Permissions.ModifyPortalContent, 'convertToBaseFormat')
  def convertToBaseFormat(self, **kw):
    """
      Converts the content of the document to a base format
      which is later used for all conversions. This method
      is common to all kinds of documents and handles
      exceptions in a unified way.

      Implementation is delegated to _convertToBaseFormat which
      must be overloaded by subclasses of Document which
      need a base format.

      convertToBaseFormat is called upon file upload, document
      ingestion by the processing_status_workflow.

      NOTE: the data of the base format conversion should be stored
      using the base_data property. Refer to Document.py propertysheet.
      Use accessors (getBaseData, setBaseData, hasBaseData, etc.)
    """
    if getattr(self, 'hasData', None) is not None and not self.hasData():
      # Empty document cannot be converted
      return
    try:
      message = self._convertToBaseFormat() # Call implemetation method
      self.clearConversionCache() # Conversion cache is now invalid
      if message is None:
        # XXX Need to translate.
        message = 'Converted to %s.' % self.getBaseContentType()
      self.convertFile(comment=message) # Invoke workflow method
    except NotImplementedError:
      message = ''
    return message

  def _convertToBaseFormat(self):
    """
    """
    raise NotImplementedError

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getMetadataMappingDict')
  def getMetadataMappingDict(self):
    """
    Return a dict of metadata mapping used to update base metadata of the
    document
    """
    try:
      method = self._getTypeBasedMethod('getMetadataMappingDict')
    except KeyError, AttributeError:
      method = None
    if method is not None:
      return method()
    else:
      return {}
  
  security.declareProtected(Permissions.ModifyPortalContent, 'updateBaseMetadata')
  def updateBaseMetadata(self, **kw):
    """
    Update the base format data with the latest properties entered
    by the user. For example, if title is changed in ERP5 interface,
    the base format file should be updated accordingly.

    Default implementation does nothing. Refer to OOoDocument class
    for an example of implementation.
    """
    pass  