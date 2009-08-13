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

import xmlrpclib, base64, re, zipfile, cStringIO
from warnings import warn
from xmlrpclib import Fault
from xmlrpclib import Transport
from xmlrpclib import SafeTransport
from AccessControl import ClassSecurityInfo
from AccessControl import Unauthorized
from OFS.Image import Pdata
from OFS.Image import File as OFSFile
from OFS.content_types import guess_content_type
from Products.CMFCore.utils import getToolByName, _setCacheHeaders,\
    _ViewEmulator
from Products.ERP5Type import Permissions, PropertySheet, Constraint
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.UnrestrictedMethod import UnrestrictedMethod
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import PermanentURLMixIn
from Products.ERP5.Document.Document import ConversionCacheMixin
from Products.ERP5.Document.Document import ConversionError
from Products.ERP5.Document.Document import NotConvertedError
from zLOG import LOG, ERROR

enc=base64.encodestring
dec=base64.decodestring

_MARKER = []
STANDARD_IMAGE_FORMAT_LIST = ('png', 'jpg', 'gif', 'tiff', )

class TimeoutTransport(SafeTransport):
  """A xmlrpc transport with configurable timeout.
  """
  def __init__(self, timeout=None, scheme='http'):
    self._timeout = timeout
    self._scheme = scheme

  def send_content(self, connection, request_body):
    connection.putheader("Content-Type", "text/xml")
    connection.putheader("Content-Length", str(len(request_body)))
    connection.endheaders()
    if self._timeout:
      connection._conn.sock.settimeout(self._timeout)
    if request_body:
      connection.send(request_body)

  def make_connection(self, h):
    if self._scheme == 'http':
      return Transport.make_connection(self, h)
    return SafeTransport.make_connection(self, h)


class OOoDocument(PermanentURLMixIn, File, ConversionCacheMixin):
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
  isPortalContent = 1
  isRADContent = 1

  searchable_property_list = ('asText', 'title', 'description', 'id', 'reference',
                              'version', 'short_title',
                              'subject', 'source_reference', 'source_project_title',)

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
                    , PropertySheet.Snapshot
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.Periodicity
                    )

  # regular expressions for stripping xml from ODF documents
  rx_strip = re.compile('<[^>]*?>', re.DOTALL|re.MULTILINE)
  rx_compr = re.compile('\s+')

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSupportBaseDataConversion')
  def isSupportBaseDataConversion(self):
    """
    OOoDocument is needed to conversion to base format.
    """
    return True

  def _setFile(self, data, precondition=None):
    File._setFile(self, data, precondition=precondition)
    if self.hasBaseData():
      # This is a hack - XXX - new accessor needed to delete properties
      try:
        delattr(self, 'base_data')
      except AttributeError:
        pass

  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, format=None, display=None, **kw):
    """
      Default renderer with conversion support. Format is
      a string. The list of available formats can be obtained
      by calling getTargetFormatItemList.
    """
    # Accelerate rendering in Web mode
    _setCacheHeaders(_ViewEmulator().__of__(self), {'format' : format})

    # Verify that the format is acceptable (from permission point of view)
    method = self._getTypeBasedMethod('checkConversionFormatPermission', 
        fallback_script_id = 'Document_checkConversionFormatPermission')
    if not method(format=format):
      raise Unauthorized("OOoDocument: user does not have enough permission to access document"
                         " in %s format" % (format or 'original'))

    # Return the original file by default
    if self.getSourceReference() is not None:
      filename = self.getSourceReference()
    else:
      filename = self.getId()
    if format is None:
      RESPONSE.setHeader('Content-Disposition',
                         'attachment; filename="%s"' % filename)
      return File.index_html(self, REQUEST, RESPONSE)
    # Make sure file is converted to base format
    if not self.hasBaseData():
      raise NotConvertedError
    # Else try to convert the document and return it
    mime, result = self.convert(format=format, display=display, **kw)
    converted_filename = '%s.%s'%(filename.split('.')[0],  format)
    if not mime:
      mime = getToolByName(self, 'mimetypes_registry').lookupExtension('name.%s' % format)
    RESPONSE.setHeader('Content-Length', len(result))
    RESPONSE.setHeader('Content-Type', mime)
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
    RESPONSE.setHeader('Content-Disposition',
                       'attachment; filename="%s"' % converted_filename)
    return result

  # Format conversion implementation
  def _getServerCoordinate(self):
    """
      Returns the oood conversion server coordinates
      as defined in preferences.
    """
    preference_tool = getToolByName(self, 'portal_preferences')
    address = preference_tool.getPreferredOoodocServerAddress()
    port = preference_tool.getPreferredOoodocServerPortNumber()
    if address in ('', None) or port in ('', None) :
      raise ConversionError('OOoDocument: can not proceed with conversion:'
            ' conversion server host and port is not defined in preferences')
    return address, port

  def _mkProxy(self):
    """
      Create an XML-RPC proxy to access the conversion server.
    """
    server_proxy = xmlrpclib.ServerProxy(
             'http://%s:%d' % self._getServerCoordinate(),
             allow_none=True,
             transport=TimeoutTransport(timeout=360, scheme='http'))
    return server_proxy

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
      raise NotConvertedError

    def cached_getTargetFormatItemList(content_type):
      server_proxy = self._mkProxy()
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
                                " formats for conversion: %s (%s)" % (
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

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatTitleList')
  def getTargetFormatTitleList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[0], self.getTargetFormatItemList())

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getTargetFormatList')
  def getTargetFormatList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[1], self.getTargetFormatItemList())

  security.declareProtected(Permissions.ModifyPortalContent,
                            'isTargetFormatAllowed')
  def isTargetFormatAllowed(self, format):
    """
      Checks if the current document can be converted
      into the specified target format.
    """
    return format in self.getTargetFormatList()

  security.declarePrivate('_convert')
  def _convert(self, format):
    """
      Communicates with server to convert a file 
    """
    if not self.hasBaseData():
      raise NotConvertedError
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
    server_proxy = self._mkProxy()
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
  security.declareProtected(Permissions.View, 'convert')
  def convert(self, format, display=None, **kw):
    """Convert the document to the given format.

    If a conversion is already stored for this format, it is returned
    directly, otherwise the conversion is stored for the next time.
    """
    #XXX if document is empty, stop to try to convert.
    #XXX but I don't know what is a appropriate mime-type.(Yusei)
    if self.get_size() == 0:
      return 'text/plain', ''

    # Make sure we can support html and pdf by default
    is_html = 0
    requires_pdf_first = 0
    original_format = format
    if format == 'base-data':
      if not self.hasBaseData():
        raise NotConvertedError
      return self.getBaseContentType(), str(self.getBaseData())
    if format == 'pdf':
      format_list = [x for x in self.getTargetFormatList()
                                          if x.endswith('pdf')]
      format = format_list[0]
    elif format in STANDARD_IMAGE_FORMAT_LIST:
      format_list = [x for x in self.getTargetFormatList()
                                          if x.endswith(format)]
      if len(format_list):
        format = format_list[0]
      else:
        # We must fist make a PDF
        requires_pdf_first = 1
        format_list = [x for x in self.getTargetFormatList()
                                          if x.endswith('pdf')]
        format = format_list[0]
    elif format == 'html':
      format_list = [x for x in self.getTargetFormatList()
                              if x.startswith('html') or x.endswith('html')]
      format = format_list[0]
      is_html = 1
    elif format in ('txt', 'text', 'text-content'):
      format_list = self.getTargetFormatList()
      # if possible, we try to get utf8 text. ('enc.txt' will encode to utf8)
      if 'enc.txt' in format_list:
        format = 'enc.txt'
      elif format not in format_list:
        return self.asTextContent()
    # Raise an error if the format is not supported
    if not self.isTargetFormatAllowed(format):
      raise ConversionError("OOoDocument: target format %s is not supported" % format)
    # Check if we have already a base conversion
    if not self.hasBaseData():
      raise NotConvertedError
    # Return converted file
    if requires_pdf_first:
      # We should use original_format whenever we wish to
      # display an image version of a document which needs to go
      # through PDF
      if display is None:
        has_format = self.hasConversion(format=original_format)
      else:
        has_format = self.hasConversion(format=original_format, display=display)
    elif display is None or original_format not in STANDARD_IMAGE_FORMAT_LIST:
      has_format = self.hasConversion(format=original_format)
    else:
      has_format = self.hasConversion(format=original_format, display=display)
    if not has_format:
      # Do real conversion
      mime, data = self._convert(format)
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
      if (display is None or original_format not in STANDARD_IMAGE_FORMAT_LIST) \
        and not requires_pdf_first:
        self.setConversion(data, mime, format=original_format)
      else:
        temp_image = self.portal_contributions.newContent(
                                       portal_type='Image',
                                       temp_object=1)
        temp_image._setData(data)
        mime, data = temp_image.convert(original_format, display=display)
        if requires_pdf_first:
          if display is None:
            self.setConversion(data, mime, format=original_format)
          else:
            self.setConversion(data, mime, format=original_format, display=display)
        else:
          if display is None:
            self.setConversion(data, mime, format=original_format)
          else:
            self.setConversion(data, mime, format=original_format, display=display)
    if requires_pdf_first:
      format = original_format
    if display is None or original_format not in STANDARD_IMAGE_FORMAT_LIST:
      return self.getConversion(format=original_format)
    else:
      return self.getConversion(format=original_format, display=display)

  security.declareProtected(Permissions.View, 'asTextContent')
  def asTextContent(self):
    """
      Extract plain text from ooo docs by stripping the XML file.
      This is the simplest way, the most universal and it is compatible
      will all formats.
    """
    return self._convert(format='text-content')

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
      mime, data = self._convert(format)
      archive_file = cStringIO.StringIO()
      archive_file.write(str(data))
      zip_file = zipfile.ZipFile(archive_file)
      must_close = 1
    else:
      must_close = 0
    for f in zip_file.infolist():
      file_name = f.filename
      document = self.get(file_name, None)
      if document is not None:
        self.manage_delObjects([file_name]) # For compatibility with old implementation
      if file_name.endswith('html'):
        mime = 'text/html'
        data = zip_file.read(file_name)
      else:
        mime = guess_content_type(file_name)[0]
        data = Pdata(zip_file.read(file_name))
      self.setConversion(data, mime=mime, format='_embedded', file_name=file_name)
    if must_close:
      zip_file.close()
      archive_file.close()

  def _getExtensibleContent(self, request, name):
    try:
      mime, data = self.getConversion(format='_embedded', file_name=name)
      return OFSFile(name, name, data, content_type=mime).__of__(self.aq_parent)
    except KeyError:
      return PermanentURLMixIn._getExtensibleContent(self, request, name)

  # Base format implementation
  security.declareProtected(Permissions.AccessContentsInformation, 'hasBaseData')
  def hasBaseData(self):
    """
      OOo instances implement conversion to a base format. We should therefore
      use the default accessor.
    """
    return self._baseHasBaseData()

  security.declarePrivate('_convertToBaseFormat')
  def _convertToBaseFormat(self):
    """
      Converts the original document into ODF
      by invoking the conversion server. Store the result
      on the object. Update metadata information.
    """
    server_proxy = self._mkProxy()
    response_code, response_dict, response_message = server_proxy.run_convert(
                                      self.getSourceReference() or self.getId(),
                                      enc(str(self.getData())))
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
                "OOoDocument: Error converting document to base format %s:%s:"
                                       % (response_code, response_message))

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getContentInformation')
  def getContentInformation(self):
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
      raise NotConvertedError

    self.clearConversionCache()

    server_proxy = self._mkProxy()
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
      raise ConversionError("OOoDocument: error getting document metadata %s:%s"
                        % (response_code, response_message))
