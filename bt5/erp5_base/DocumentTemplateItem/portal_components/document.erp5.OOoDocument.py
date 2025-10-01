# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
# Copyright (c) 2006-2007 Nexedi SA and Contributors. All Rights Reserved.
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

import contextlib
import re, zipfile
from io import BytesIO
import six
from warnings import warn
from AccessControl import ClassSecurityInfo
from OFS.Image import Pdata
from zope.contenttype import guess_content_type
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Cache import CachingMethod
from erp5.component.document.File import File
from erp5.component.document.Document import ConversionError, Document, \
       VALID_IMAGE_FORMAT_LIST, VALID_TEXT_FORMAT_LIST
from Products.ERP5Type.Utils import (guessEncodingFromText,
                                     bytes2str,
                                     fill_args_from_request,
                                     str2bytes,
                                     unicode2str)

# Mixin Import
from erp5.component.mixin.TextConvertableMixin import TextConvertableMixin
from erp5.component.mixin.OOoDocumentExtensibleTraversableMixin import OOoDocumentExtensibleTraversableMixin

EMBEDDED_FORMAT = '_embedded'

from erp5.component.document.Document import DocumentConversionServerProxy
# Backward compatibility only
from erp5.component.document.Document import DOCUMENT_CONVERSION_SERVER_PROXY_TIMEOUT as OOO_SERVER_PROXY_TIMEOUT # pylint: disable=unused-import
from erp5.component.document.Document import DOCUMENT_CONVERSION_SERVER_RETRY as OOO_SERVER_RETRY # pylint: disable=unused-import
from erp5.component.document.Document import global_server_proxy_uri_failure_time # pylint: disable=unused-import
from erp5.component.document.Document import enc, dec
OOoServerProxy = DocumentConversionServerProxy

class OOoDocument(OOoDocumentExtensibleTraversableMixin, TextConvertableMixin, File, Document):
  """
    A file document able to convert OOo compatible files to
    any OOo supported format, to capture metadata and to
    update metadata in OOo documents.

    This class can be used:

    - to create an OOo document database with powerful indexing (r/o)
      and metadata handling (r/w) features (ex. change title in ERP5 ->
      title is changed in OOo document)

    - to massively convert MS Office documents to OOo format

    - to easily keep snapshots (in PDF and/or OOo format) of OOo documents
      generated from OOo templates

    This class may be used in the future:

    - to create editable OOo templates (ex. by adding tags in WYSIWYG mode
      and using tags to make document dynamic - ask kevin for more info)

    - to automatically sign / encrypt OOo documents based on user

    - to automatically sign / encrypt PDF generated from OOo documents based on user

    This class should not be used:

    - to store files in formats not supported by OOo

    - to stored pure images (use Image for that)

    - as a general file conversion system (use portal_transforms for that)

    TODO:
    - better permissions
  """
  # CMF Type Definition
  meta_type = 'ERP5 OOo Document'
  portal_type = 'OOo Document'

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Default Properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.Reference
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Document
                    , PropertySheet.Data
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
                    , PropertySheet.SortIndex
                    )

  # regular expressions for stripping xml from ODF documents
  rx_strip = re.compile(r'<[^>]*?>', re.DOTALL|re.MULTILINE)
  rx_compr = re.compile(r'\s+')

  security.declareProtected(Permissions.View, 'index_html')
  @fill_args_from_request('display', 'quality', 'resolution')
  def index_html(self, REQUEST, *args, **kw):
    """Return the document data."""
    return Document.index_html(self, REQUEST, *args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSupportTextConversion')
  def isSupportTextConversion(self):
    """
    OOoDocument is needed to conversion to base format.
    """
    return True

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatItemList')
  def getTargetFormatItemList(self):
    """
      Returns a list of acceptable formats for conversion
      in the form of tuples (for listfield in ERP5Form)

      NOTE: it is the responsability of the conversion server
      to provide an extensive list of conversion formats.
    """
    def cached_getTargetFormatItemList(content_type):
      from six.moves.xmlrpc_client import Fault
      server_proxy = DocumentConversionServerProxy(self)
      # Coerce Content-Type as a string when falsy, otherwise Cloudooo returns
      # Code 402: expected str, bytes or os.PathLike object, not NoneType
      content_type = content_type or ""
      try:
        allowed_target_item_list = server_proxy.getAllowedTargetItemList(
                                                      content_type)
        try:
          response_code, response_dict, response_message = \
                                             allowed_target_item_list
        except ValueError:
          # Compatibility with older oood where getAllowedTargetItemList only
          # returned response_dict
          response_code, response_dict, response_message = \
                         200, dict(response_data=allowed_target_item_list), ''

        if response_code == 200:
          allowed = response_dict['response_data']
        else:
          # This is very temporary code - XXX needs to be changed
          # so that the system can retry
          raise ConversionError("OOoDocument: can not get list of allowed acceptable"
                                " formats for conversion (Code %s: %s)" % (
                                      response_code, response_message))

      except Fault:
        allowed = server_proxy.getAllowedTargets(content_type)
        warn('Your oood version is too old, using old method '
            'getAllowedTargets instead of getAllowedTargetList',
             DeprecationWarning)
      finally:
        server_proxy.close()
      # tuple order is reversed to be compatible with ERP5 Form
      return [(y, x) for x, y in allowed]

    # Cache valid format list
    cached_getTargetFormatItemList = CachingMethod(
                                cached_getTargetFormatItemList,
                                id="OOoDocument_getTargetFormatItemList",
                                cache_factory='erp5_ui_medium')

    return cached_getTargetFormatItemList(self.getContentType())

  def _getConversionFromProxyServer(self, format): #  pylint: disable=redefined-builtin
    """
      Communicates with server to convert a file
    """
    with contextlib.closing(DocumentConversionServerProxy(self)) as server_proxy:
      # XXX: not very nice, as we once more refer to base data...
      proxy_function = server_proxy.run_convert if format == None else server_proxy.run_generate
      generate_result = proxy_function(self.getId(),
                                       bytes2str(enc(bytes(self.getData()))),
                                       None,
                                       format,
                                       self.getContentType())
    try:
      _, response_dict, _ = generate_result
    except ValueError:
      # This is for backward compatibility with older oood version returning
      # only response_dict
      response_dict = generate_result

    # XXX: handle possible OOOd server failure
    return response_dict['mime'], Pdata(dec(str2bytes(response_dict['data'])))

  def _convert(self, format, frame=0, **kw): # pylint: disable=redefined-builtin
    """
    Convert document to the given format.

    Constraints for this functions are: there are two cases where we need
    cascading conversion (ie. conversion to an intermediate format), and the
    conversion cache should be used as efficiently as possible. At the end, the
    process is rather convoluted to get the final result.
    """
    # XXX-Yusei: if document is empty, stop to try to convert,
    # but I don't know what is an appropriate mime-type.
    if not self.hasData():
      return 'text/plain', ''
    # If no conversion asked (format empty), return raw data
    if not format:
      return self.getContentType(), self.getData()

    # Use cache early: if document was converted before, return it
    # XXX-Titouan: that means we might end up with same conversion twice
    # in the cache, if two format give the same result.
    if self.hasConversion(format=format, **kw):
      return self.getConversion(format=format, **kw)

    # We deal with three different format variables: `original_format`, as
    # requested by the caller, which is always the key used for cache ;
    # `format`, given to Cloudooo for conversion (usually derived from
    # `original_format`) and `intermediate_format` when we need a conversion
    # chain (OOoDocument -> PDF -> Image).
    original_format = format
    to_image = False
    to_unzipped = False
    allowed_format_list = self.getTargetFormatList()
    if format == 'pdf':
      format_list = [x for x in allowed_format_list
                                          if x.endswith('pdf')]
      format = format_list[0]
    elif format in VALID_IMAGE_FORMAT_LIST:
      format_list = [x for x in allowed_format_list
                                          if x.endswith(format)]
      if len(format_list):
        format = format_list[0]
      else:
        # We must first make a PDF which will be used to produce an image out of it
        format_list = [x for x in allowed_format_list
                                          if x.endswith('pdf')]
        format = format_list[0]
        to_image = True
    elif format == 'html':
      format_list = [x for x in allowed_format_list
                              if x.startswith('html') or x.endswith('html')]
      format = format_list[0]
      to_unzipped = True
    elif format in ('txt', 'text', 'text-content'):
      # One exception to the always-store-conversion-as-original rule
      original_format = 'txt'
      # If possible, we try to get utf8 text
      if 'enc.txt' in allowed_format_list:
        format = 'enc.txt'
      elif format not in allowed_format_list:
        # `format = None` is different from `intermediate_format = None`.
        # The latter indicates no intermediate conversion, while the former
        # is conversion to what was base format before (ODS, ODT, etc).
        format = None
        to_unzipped = True

    if format is not None and \
        not self.isTargetFormatAllowed(format):
      raise ConversionError("OOoDocument: target format %s is not supported" % format)

    mime, data = self._getConversionFromProxyServer(format)

    # Conversion chain for OOo -> PDF -> Image
    if to_image:
      # Create temporary image and use it to resize accordingly
      temp_image = self.portal_contributions.newContent(
        portal_type='Image',
        file=BytesIO(),
        filename=self.getId(),
        temp_object=1,
      )
      temp_image._setData(data)
      # We care for first page only but as well for image quality
      mime, data = temp_image.convert(original_format, frame=frame, **kw)

    if to_unzipped:
      cs = BytesIO()
      cs.write(bytes(data)) # Cast explicitly to bytes for possible Pdata
      z = zipfile.ZipFile(cs) # A disk file would be more RAM efficient
      # Conversion chain for OOo -> ODF -> Text: extract
      # text from the ODF file.
      if format is None:
        data = bytes2str(z.read('content.xml'))
        data = self.rx_strip.sub(" ", data) # strip xml
        data = self.rx_compr.sub(" ", data) # compress multiple spaces
        mime = 'text/plain'
      # Special case for OOo -> HTML
      else:
        for f in z.infolist():
          fn = f.filename
          if fn.endswith('html'):
            if self.getPortalType() == 'Presentation'\
                  and not (fn.find('impr') >= 0):
              continue
            data = z.read(fn)
            break
        mime = 'text/html'
        # XXX: Maybe some parts should be asynchronous for better usability
        self._populateConversionCacheWithHTML(zip_file=z)
      z.close()
      cs.close()

    self.setConversion(data, mime, format=original_format, **kw)
    # We have to recourse to `getConversion` every time, even if we already own
    # an handle to converted data because CacheConvertableMixin does type
    # conversion (ie. Pdata to bytes), and it should not be predicted manually.
    mime, data = self.getConversion(format=original_format, **kw)

    if format in VALID_TEXT_FORMAT_LIST:
      # Libreoffice conversions on cloudooo usually have a BOM, we are using guessEncodingFromText
      # here mostly as a convenient way to decode with the encoding from BOM
      data = data.decode(guessEncodingFromText(data) or 'ascii')
      if six.PY2:
        data = unicode2str(data)
    return mime, data

  security.declareProtected(Permissions.ModifyPortalContent,
                            '_populateConversionCacheWithHTML')
  def _populateConversionCacheWithHTML(self, zip_file=None):
    """
    Extract content from the ODF zip file and populate the document.
    Optional parameter zip_file prevents from converting content twice.
    """
    if zip_file is None:
      format_list = [x for x in self.getTargetFormatList()
                                if x.startswith('html') or x.endswith('html')]
      mime, data = self._getConversionFromProxyServer(format_list[0])
      archive_file = BytesIO()
      archive_file.write(data)
      zip_file = zipfile.ZipFile(archive_file)
      must_close = 1
    else:
      must_close = 0
    for f in zip_file.infolist():
      filename = f.filename
      document = self.get(filename, None)
      if document is not None:
        self.manage_delObjects([filename]) # For compatibility with old implementation
      if filename.endswith('html'):
        mime = 'text/html'
        # call portal_transforms to strip HTML in safe mode
        portal = self.getPortalObject()
        transform_tool = getToolByName(portal, 'portal_transforms')
        data = transform_tool.convertToData('text/x-html-safe',
                                            zip_file.read(filename),
                                            object=self, context=self,
                                            mimetype=mime)
      else:
        mime = guess_content_type(filename)[0]
        data = Pdata(zip_file.read(filename))
      self.setConversion(data, mime=mime, format=EMBEDDED_FORMAT, filename=filename)
    if must_close:
      zip_file.close()
      archive_file.close()

  def _getContentInformation(self):
    """
      Returns the metadata extracted by the conversion
      server.
    """
    return getattr(self, '_document_metadata', {})

  security.declareProtected(Permissions.ModifyPortalContent, 'eraseLocalMetadata')
  def eraseLocalMetadata(self):
    self._document_metadata = {}

  security.declareProtected(Permissions.ModifyPortalContent, 'updateLocalMetadataFromDocument')
  def updateLocalMetadataFromDocument(self, **kw):
    """
      Updates locally stored metadata (and Content Type) from
      information stored on the document.
    """
    # No metadata can be guessed from empty documents, early abort
    if not self.getData():
      return

    with contextlib.closing(DocumentConversionServerProxy(self)) as server_proxy:
      response_code, response_dict, response_message = \
          server_proxy.run_getmetadata(self.getId(),
                                       bytes2str(enc(bytes(self.getData()))),
                                       kw)

    if response_code == 200:
      metadata = response_dict['meta']
      self._document_metadata = metadata
      if metadata.get('MIMEType', None) is not None and \
          not self.hasContentType():
        self._setContentType(metadata['MIMEType'])
    else:
      raise ConversionError("OOoDocument: error getting document metadata (Code %s: %s)"
                        % (response_code, response_message))

  security.declareProtected(Permissions.ModifyPortalContent, 'updateMetadata')
  def updateMetadata(self, **kw):
    """
      Updates metadata information in the converted OOo document
      based on the values provided by the user. This is implemented
      through the invocation of the conversion server.
    """
    with contextlib.closing(DocumentConversionServerProxy(self)) as server_proxy:
      response_code, response_dict, response_message = \
          server_proxy.run_setmetadata(self.getId(),
                                       bytes2str(enc(bytes(self.getData()))),
                                       kw)
    if response_code == 200:
      # successful meta data extraction
      self._setData(dec(str2bytes(response_dict['data'])))
      self.getPortalObject().portal_workflow.doActionFor(self, action="edit_action", comment="Updated file metadata")
    else:
      # Explicitly raise the exception!
      raise ConversionError("OOoDocument: error setting document metadata (Code %s: %s)"
                        % (response_code, response_message))
