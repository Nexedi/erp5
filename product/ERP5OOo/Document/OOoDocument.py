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

import re, zipfile, cStringIO
from warnings import warn
from AccessControl import ClassSecurityInfo
from OFS.Image import Pdata
from zope.contenttype import guess_content_type
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import Document, \
       VALID_IMAGE_FORMAT_LIST, ConversionError, NotConvertedError
from Products.ERP5Type.Utils import fill_args_from_request

# Mixin Import
from Products.ERP5.mixin.base_convertable import BaseConvertableFileMixin
from Products.ERP5.mixin.text_convertable import TextConvertableMixin
from Products.ERP5.mixin.extensible_traversable import OOoDocumentExtensibleTraversableMixin

EMBEDDED_FORMAT = '_embedded'

from Products.ERP5.Document.Document import DocumentConversionServerProxy
# Backward compatibility only
from Products.ERP5.Document.Document import DOCUMENT_CONVERSION_SERVER_PROXY_TIMEOUT as OOO_SERVER_PROXY_TIMEOUT
from Products.ERP5.Document.Document import DOCUMENT_CONVERSION_SERVER_RETRY as OOO_SERVER_RETRY
from Products.ERP5.Document.Document import global_server_proxy_uri_failure_time
from Products.ERP5.Document.Document import enc, dec
OOoServerProxy = DocumentConversionServerProxy

class OOoDocument(OOoDocumentExtensibleTraversableMixin, BaseConvertableFileMixin, File,
                  TextConvertableMixin, Document):
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
  rx_strip = re.compile('<[^>]*?>', re.DOTALL|re.MULTILINE)
  rx_compr = re.compile('\s+')

  security.declareProtected(Permissions.View, 'index_html')
  @fill_args_from_request('display', 'quality', 'resolution')
  def index_html(self, REQUEST, *args, **kw):
    """Return the document data."""
    return Document.index_html(self, REQUEST, *args, **kw)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSupportBaseDataConversion')
  def isSupportBaseDataConversion(self):
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
    if not self.hasBaseData():
      # if we have no date we can not format it
      return []

    def cached_getTargetFormatItemList(content_type):
      from xmlrpclib import Fault
      server_proxy = DocumentConversionServerProxy(self)
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

      except Fault, f:
        allowed = server_proxy.getAllowedTargets(content_type)
        warn('Your oood version is too old, using old method '
            'getAllowedTargets instead of getAllowedTargetList',
             DeprecationWarning)

      # tuple order is reversed to be compatible with ERP5 Form
      return [(y, x) for x, y in allowed]

    # Cache valid format list
    cached_getTargetFormatItemList = CachingMethod(
                                cached_getTargetFormatItemList,
                                id="OOoDocument_getTargetFormatItemList",
                                cache_factory='erp5_ui_medium')

    return cached_getTargetFormatItemList(self.getBaseContentType())

  def _getConversionFromProxyServer(self, format):
    """
      Communicates with server to convert a file
    """
    if not self.hasBaseData():
      # XXX please pass a meaningful description of error as argument
      raise NotConvertedError()
    if format == 'text-content':
      # Extract text from the ODF file
      cs = cStringIO.StringIO()
      cs.write(str(self.getBaseData()))
      z = zipfile.ZipFile(cs)
      s = z.read('content.xml')
      s = self.rx_strip.sub(" ", s) # strip xml
      s = self.rx_compr.sub(" ", s) # compress multiple spaces
      cs.close()
      z.close()
      return 'text/plain', s
    server_proxy = DocumentConversionServerProxy(self)
    orig_format = self.getBaseContentType()
    generate_result = server_proxy.run_generate(self.getId(),
                                       enc(str(self.getBaseData())),
                                       None,
                                       format,
                                       orig_format)
    try:
      response_code, response_dict, response_message = generate_result
    except ValueError:
      # This is for backward compatibility with older oood version returning
      # only response_dict
      response_dict = generate_result

    # XXX: handle possible OOOd server failure
    return response_dict['mime'], Pdata(dec(response_dict['data']))

  # Conversion API
  def _convert(self, format, frame=0, **kw):
    """Convert the document to the given format.

    If a conversion is already stored for this format, it is returned
    directly, otherwise the conversion is stored for the next time.

    frame: Only used for image conversion

    XXX Cascading conversions must be delegated to conversion server,
    not by OOoDocument._convert (ie: convert to pdf, then convert to image, then resize)
    *OR* as an optimisation we can read cached intermediate conversions
    instead of compute them each times.
      1- odt->pdf->png
      2- odt->cached(pdf)->jpg
    """
    #XXX if document is empty, stop to try to convert.
    #XXX but I don't know what is a appropriate mime-type.(Yusei)
    if not self.hasData():
      return 'text/plain', ''
    # if no conversion asked (format empty)
    # return raw data
    if not format:
      return self.getContentType(), self.getData()
    # Check if we have already a base conversion
    if not self.hasBaseData():
      # XXX please pass a meaningful description of error as argument
      raise NotConvertedError()
    # Make sure we can support html and pdf by default
    is_html = 0
    requires_pdf_first = 0
    original_format = format
    allowed_format_list = self.getTargetFormatList()
    if format == 'base-data':
      return self.getBaseContentType(), str(self.getBaseData())
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
        # We must fist make a PDF which will be used to produce an image out of it
        requires_pdf_first = 1
        format_list = [x for x in allowed_format_list
                                          if x.endswith('pdf')]
        format = format_list[0]
    elif format == 'html':
      format_list = [x for x in allowed_format_list
                              if x.startswith('html') or x.endswith('html')]
      format = format_list[0]
      is_html = 1
    elif format in ('txt', 'text', 'text-content'):
      # if possible, we try to get utf8 text. ('enc.txt' will encode to utf8)
      if 'enc.txt' in allowed_format_list:
        format = 'enc.txt'
      elif format not in allowed_format_list:
        #Text conversion is not supported by oood, do it in other way
        if not self.hasConversion(format=original_format):
          #Do real conversion for text
          mime, data = self._getConversionFromProxyServer(format='text-content')
          self.setConversion(data, mime, format=original_format)
          return mime, data
        return self.getConversion(format=original_format)
    # Raise an error if the format is not supported
    if not self.isTargetFormatAllowed(format):
      raise ConversionError("OOoDocument: target format %s is not supported" % format)
    has_format = self.hasConversion(format=original_format, **kw)
    if not has_format:
      # Do real conversion
      mime, data = self._getConversionFromProxyServer(format)
      if is_html:
        # Extra processing required since
        # we receive a zip file
        cs = cStringIO.StringIO()
        cs.write(str(data))
        z = zipfile.ZipFile(cs) # A disk file would be more RAM efficient
        for f in z.infolist():
          fn = f.filename
          if fn.endswith('html'):
            if self.getPortalType() == 'Presentation'\
                  and not (fn.find('impr') >= 0):
              continue
            data = z.read(fn)
            break
        mime = 'text/html'
        self._populateConversionCacheWithHTML(zip_file=z) # Maybe some parts should be asynchronous for
                                         # better usability
        z.close()
        cs.close()
      if original_format not in VALID_IMAGE_FORMAT_LIST \
        and not requires_pdf_first:
        self.setConversion(data, mime, format=original_format, **kw)
      else:
        # create temporary image and use it to resize accordingly
        temp_image = self.portal_contributions.newContent(
                                       portal_type='Image',
                                       file=cStringIO.StringIO(),
                                       filename=self.getId(),
                                       temp_object=1)
        temp_image._setData(data)
        # we care for first page only but as well for image quality
        mime, data = temp_image.convert(original_format, frame=frame, **kw)
        # store conversion
        self.setConversion(data, mime, format=original_format, **kw)

    return self.getConversion(format=original_format, **kw)

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
      format = format_list[0]
      mime, data = self._getConversionFromProxyServer(format)
      archive_file = cStringIO.StringIO()
      archive_file.write(str(data))
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

  security.declarePrivate('_convertToBaseFormat')
  def _convertToBaseFormat(self):
    """
      Converts the original document into ODF
      by invoking the conversion server. Store the result
      on the object. Update metadata information.
    """
    server_proxy = DocumentConversionServerProxy(self)
    response_code, response_dict, response_message = server_proxy.run_convert(
                                      self.getFilename() or self.getId(),
                                      enc(str(self.getData())),
                                      None,
                                      None,
                                      self.getContentType())
    if response_code == 200:
      # sucessfully converted document
      self._setBaseData(dec(response_dict['data']))
      metadata = response_dict['meta']
      self._base_metadata = metadata
      if metadata.get('MIMEType', None) is not None:
        self._setBaseContentType(metadata['MIMEType'])
    else:
      # Explicitly raise the exception!
      raise ConversionError(
                "OOoDocument: Error converting document to base format. (Code %s: %s)"
                                       % (response_code, response_message))

  def _getContentInformation(self):
    """
      Returns the metadata extracted by the conversion
      server.
    """
    return getattr(self, '_base_metadata', {})

  security.declareProtected(Permissions.ModifyPortalContent,
                            'updateBaseMetadata')
  def updateBaseMetadata(self, **kw):
    """
      Updates metadata information in the converted OOo document
      based on the values provided by the user. This is implemented
      through the invocation of the conversion server.
    """
    if not self.hasBaseData():
      # XXX please pass a meaningful description of error as argument
      raise NotConvertedError()

    server_proxy = DocumentConversionServerProxy(self)
    response_code, response_dict, response_message = \
          server_proxy.run_setmetadata(self.getId(),
                                       enc(str(self.getBaseData())),
                                       kw)
    if response_code == 200:
      # successful meta data extraction
      self._setBaseData(dec(response_dict['data']))
      self.updateFileMetadata() # record in workflow history # XXX must put appropriate comments.
    else:
      # Explicitly raise the exception!
      raise ConversionError("OOoDocument: error getting document metadata (Code %s: %s)"
                        % (response_code, response_message))
