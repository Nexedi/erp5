##############################################################################
#
# Copyright (c) 2002 Nexedi SARL and Contributors. All Rights Reserved.
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

import zope.interface

import mimetypes
import re

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Base import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5.Document.Document import Document
from Products.ERP5.Document.Document import ConversionCacheMixin
from Products.ERP5.Document.Document import ConversionError
from Products.ERP5Type.Base import Base
from Products.CMFDefault.File import File as CMFFile
from zLOG import LOG
from DateTime import DateTime

mimetypes.init()

def _unpackData(data):
  """
  Unpack Pdata into string
  """
  if isinstance(data, str):
    return data
  else:
    data_list = []
    while data is not None:
      data_list.append(data.data)
      data = data.next
    return ''.join(data_list)

class File(Document, CMFFile, ConversionCacheMixin):
  """
      A File can contain raw data which can be uploaded and downloaded.
      It is the root class of Image, OOoDocument (ERP5OOo product),
      etc. The main purpose of the File class is to handle efficiently
      large files. It uses Pdata from OFS.File for this purpose.

      File inherits from XMLObject and can be synchronized
      accross multiple sites.

      Subcontent: File can only contain role information.

      TODO:
      * make sure ZODB BLOBS are supported to prevent
       feeding the ZODB cache with unnecessary large data
  """

  meta_type = 'ERP5 File'
  portal_type = 'File'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default global values
  content_type = '' # Required for WebDAV support (default value)
  data = '' # A hack required to use OFS.Image.index_html without calling OFS.Image.__init__

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Reference
                    , PropertySheet.Document
                    , PropertySheet.Data
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
    )

  searchable_property_list = ('title', 'description', 'id', 'reference',
                              'version', 'short_title',
                              'subject', 'source_reference', 'source_project_title',)

  # Declarative interfaces
  #zope.interface.implements( , )

  ### Special edit method
  security.declarePrivate( '_edit' )
  def _edit(self, set_filename__=1, **kw):
    """\
      This is used to edit files
    """
    if kw.has_key('file'):
      file = kw.get('file')
      precondition = kw.get('precondition')
      if self._isNotEmpty(file):
        self._setFile(file, precondition=precondition)
      if set_filename__:
        filename = getattr(file, 'filename', None)
        # if file field is empty(no file is uploaded),
        # filename is empty string.
        if filename not in (None, ''):
          kw['source_reference'] = filename
      del kw['file']
    Base._edit(self, **kw)

  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  edit = WorkflowMethod( _edit )

  def get_size(self):
    """
    has to be overwritten here, otherwise WebDAV fails
    """
    data_len = len(getattr(self, 'data', ''))
    if not data_len:
      data_len = len(self.getBaseData() or '')
    return data_len

  getcontentlength = get_size

  def _setFile(self, data, precondition=None):
    self.clearConversionCache()
    CMFFile._edit(self, precondition=precondition, file=data)

  security.declareProtected(Permissions.ModifyPortalContent,'setFile')
  def setFile(self, data, precondition=None):
    self._setFile(data, precondition=precondition)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation, 'hasFile')
  def hasFile(self):
    """
    Checks whether a file was uploaded into the document.
    """
    return self.hasData()

  security.declareProtected(Permissions.AccessContentsInformation, 'hasBaseData')
  def hasBaseData(self):
    """
      By default, a File instance does not require conversion
      to a base format. Therefore, hasBaseData must be overriden.
    """
    return self.hasData()

  security.declareProtected(Permissions.ModifyPortalContent, 'guessMimeType')
  def guessMimeType(self, fname=''):
    """
      get mime type from file name
    """
    if fname == '': fname = self.getOriginalFilename()
    if fname:
      content_type,enc = mimetypes.guess_type(fname)
      if content_type is not None:
        self.content_type = content_type
    return content_type

  security.declareProtected(Permissions.ModifyPortalContent,'PUT')
  def PUT(self, REQUEST, RESPONSE):
    self.clearConversionCache()
    CMFFile.PUT(self, REQUEST, RESPONSE)

  # DAV Support
  index_html = CMFFile.index_html 
  PUT = CMFFile.PUT
  security.declareProtected('FTP access', 'manage_FTPget', 'manage_FTPstat', 'manage_FTPlist')
  manage_FTPget = CMFFile.manage_FTPget
  manage_FTPlist = CMFFile.manage_FTPlist
  manage_FTPstat = CMFFile.manage_FTPstat

  security.declareProtected(Permissions.AccessContentsInformation, 'getMimeTypeAndContent')
  def getMimeTypeAndContent(self):
    """This method returns a tuple which contains mimetype and content."""
    from Products.ERP5.Document.EmailDocument import MimeTypeException
    # return a tuple (mime_type, data)
    mime_type = None
    content = None

    # WARNING - this could fail since getContentType
    # is not (yet) part of Document API
    if getattr(self, 'getContentType', None) is not None:
      mime_type = self.getContentType()
    elif getattr(self, 'getTextFormat', None) is not None:
      mime_type = self.getTextFormat()
    else:
      raise ValueError, "Cannot find mimetype of the document."

    if mime_type is not None:
      try:
        mime_type, content = self.convert(mime_type)
      except ConversionError:
        mime_type = self.getBaseContentType()
        content = self.getBaseData()
      except (NotImplementedError, MimeTypeException):
        pass

    if content is None:
      if getattr(self, 'getTextContent', None) is not None:
        content = self.getTextContent()
      elif getattr(self, 'getData', None) is not None:
        content = self.getData()
      elif getattr(self, 'getBaseData', None) is not None:
        content = self.getBaseData()

    if content and not isinstance(content, str):
      content = str(content)

    return (mime_type, content)

