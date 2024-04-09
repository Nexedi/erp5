# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2010 Nexedi SA and Contributors. All Rights Reserved.
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

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Base import WorkflowMethod
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.Document import Document, VALID_TEXT_FORMAT_LIST
from erp5.component.document.Document import VALID_IMAGE_FORMAT_LIST
from erp5.component.document.Document import ConversionError
from Products.ERP5Type.Base import Base, removeIContentishInterface
from OFS.Image import File as OFS_File
from Products.ERP5Type.Utils import deprecated
import six

_MARKER = object()

class File(Document, OFS_File):
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

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default global values
  data = b'' # A hack required to use OFS.Image.index_html without calling OFS.Image.__init__

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

  # OFS.File has an overloaded __str__ that returns the file content
  __str__ = object.__str__

  ### Special edit method
  security.declarePrivate( '_edit' )
  def _edit(self, **kw):
    """
      This is used to edit files
    """
    if 'file' in kw:
      file_object = kw.pop('file')
      filename = getattr(file_object, 'filename', None)
      # if file field is empty(no file is uploaded),
      # filename is empty string.
      if not filename:
        # settings the filename before calling
        # _setFile is required to setup the content_type
        # property
        filename = kw.get('filename')
      if filename:
        self._setFilename(filename)
      if file_object is not None:
        # XXX: Rather than doing nothing if empty, consider changing:
        #      - _update_image_info to clear metadata
        #      - interactions to do nothing (or else?)
        file_object.seek(0, 2)
        if file_object.tell():
          file_object.seek(0)
          self._setFile(file_object)
    Base._edit(self, **kw)

  security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
  edit = WorkflowMethod( _edit )

  security.declareProtected(Permissions.View, 'get_size')
  def get_size(self):
    """
    has to be overwritten here, otherwise WebDAV fails
    """
    return self.getSize()

  security.declareProtected(Permissions.View, 'getcontentlength')
  getcontentlength = get_size

  def _get_content_type(self, *_, **__):
    """Override original implementation from OFS/Image.py
    to disable content_type discovery because
    id of object its used to read the filename value.
    In ERP5, an interaction
    document_conversion_interaction_workflow/Document_file,
    update the content_type by reading filename property
    """
    return None

  def _setFile(self, data, precondition=None):
    if data is None:
      return
    if self.hasData():
      if bytes(data.read()) == bytes(self.getData()):
        # Same data as previous, no need to change its content
        return
    else:
      data.seek(0, 2)

    if data.tell():
      data.seek(0)
      self.manage_upload(data)

  security.declarePrivate('update_data')
  def update_data(self, *args, **kw):
    super(File, self).update_data(*args, **kw)
    if six.PY2 and isinstance(self.size, long):  # pylint:disable=undefined-variable
      self.size = int(self.size)

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

  security.declareProtected(Permissions.AccessContentsInformation, 'guessMimeType')
  @deprecated
  def guessMimeType(self, fname=None):
    """
      Deprecated
    """
    return self.getPortalObject().portal_contributions.\
      guessMimeTypeFromFilename(fname)

  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  def getData(self, default=None):
    """return Data as bytes."""
    self._checkConversionFormatPermission(None)
    data = self._baseGetData()
    if data is None:
      return None
    else:
      if six.PY3 and isinstance(data, str):
        return bytes(data, self._get_encoding())
      return bytes(data)

  # DAV Support
  security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
  def PUT(self, REQUEST, RESPONSE):
    """from Products.CMFDefault.File"""
    OFS_File.PUT(self, REQUEST, RESPONSE)
    self.reindexObject()

  security.declareProtected(Permissions.AccessContentsInformation, 'getMimeTypeAndContent')
  def getMimeTypeAndContent(self):
    # type: () -> tuple[str, bytes]
    """This method returns a tuple which contains mimetype and content."""
    from erp5.component.document.EmailDocument import MimeTypeException
    content = None
    mime_type = self.getContentType()

    if mime_type is None:
      raise ValueError('Cannot find mimetype of the document.')
    try:
      mime_type, content = self.convert(None)
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

    if isinstance(content, six.text_type):
      content = content.encode('utf-8')
    if content and not isinstance(content, bytes):
      content = bytes(content)

    return (mime_type, content)

  def _convert(self, format, **kw): # pylint: disable=redefined-builtin
    """File is only convertable if it is an image.
    Only Image conversion, original format and text formats are allowed.
    However this document can migrate to another portal_type which support
    others conversions.
    """
    content_type = self.getContentType() or ''
    if (format in VALID_IMAGE_FORMAT_LIST + (None, "")) and \
          content_type.startswith("image/"):
      # The file should behave like it is an Image for convert
      # the content to target format.
      return self.newContent(temp_object=True, portal_type='Image', id=self.getId(),
                 data=self.getData(),
                 content_type=content_type,
                 filename=self.getFilename())._convert(format, **kw)

    elif format in (None, ""):
      # No conversion is asked,
      # we can return safely the file content itself
      return content_type, self.getData()

    elif format in VALID_TEXT_FORMAT_LIST:
      # This is acceptable to return empty string
      # for a File we can not convert
      return 'text/plain', ''
    raise NotImplementedError

  # backward compatibility
  security.declareProtected(Permissions.AccessContentsInformation, 'getFilename')
  def getFilename(self, default=_MARKER):
    """Fallback on getSourceReference as it was used
    before to store filename property
    """
    if self.hasFilename():
      if default is _MARKER:
        return self._baseGetFilename()
      else:
        return self._baseGetFilename(default)
    else:
      if default is _MARKER:
        return self._baseGetSourceReference()
      else:
        return self._baseGetSourceReference(default)

# CMFFile also brings the IContentishInterface on CMF 2.2, remove it.
removeIContentishInterface(File)

