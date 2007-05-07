##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
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

import xmlrpclib, base64, re, zipfile, cStringIO, socket
from warnings import warn
from DateTime import DateTime
from xmlrpclib import Fault
from AccessControl import ClassSecurityInfo
from OFS.Image import Pdata
from Products.CMFCore.utils import getToolByName, _setCacheHeaders
from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5Type.Message import Message
from Products.ERP5Type.Cache import CachingMethod
from Products.ERP5Type.XMLObject import XMLObject
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import ConversionCacheMixin, ConversionError
from Products.ERP5.Document.File import _unpackData
from zLOG import LOG, INFO, ERROR

enc=base64.encodestring
dec=base64.decodestring

_MARKER = []
STANDARD_IMAGE_FORMAT_LIST = ('png', 'jpg', 'gif', )

class OOoDocument(File, ConversionCacheMixin):
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

  def _setFile(self, data, precondition=None):
    File._setFile(self, data, precondition=precondition)
    if self.hasBaseData():
      # This is a hack - XXX - new accessor needed to delete properties
      delattr(self, 'base_data')

  security.declareProtected(Permissions.View, 'index_html')
  def index_html(self, REQUEST, RESPONSE, format=None, display=None, **kw):
    """
      Default renderer with conversion support. Format is
      a string. The list of available formats can be obtained
      by calling getTargetFormatItemList.
    """
    # Accelerate rendering in Web mode
    _setCacheHeaders(self, {'format' : format})
    # Return the original file by default
    if format is None:
      return File.index_html(self, REQUEST, RESPONSE)
    # Make sure file is converted to base format
    if not self.hasBaseData():
      self.convertToBaseFormat()
    # Else try to convert the document and return it
    mime, result = self.convert(format=format, display=display, **kw)
    if not mime:
      mime = getToolByName(self, 'mimetypes_registry').lookupExtension('name.%s' % format)
    RESPONSE.setHeader('Content-Length', len(result))
    RESPONSE.setHeader('Content-Type', mime)
    RESPONSE.setHeader('Accept-Ranges', 'bytes')
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
    if not address or not port:
      raise ConversionError('Can not proceed with conversion: '
                            'conversion server host and port is not defined in preferences')
    return address, port

  def _mkProxy(self):
    """
      Create an XML-RPC proxy to access the conversion server.
    """
    server_proxy = xmlrpclib.ServerProxy('http://%s:%d' % self._getServerCoordinate(),
                                         allow_none=True)
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
      self.convertToBaseFormat()

    def cached_getTargetFormatItemList(content_type):
      server_proxy = self._mkProxy()
      try:
        response_code, response_dict, response_message = server_proxy.getAllowedTargetItemList(content_type)
        if response_code == 200:
          allowed = response_dict['response_data']
        else:
          # This is very temporary code - XXX needs to be changed
          # so that the system can retry
          raise ConversionError("[DMS] Can not get list of allowed acceptable formats for conversion: %s (%s)"  
                                       %(response_code, response_message))
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

  security.declareProtected(Permissions.AccessContentsInformation, 'getTargetFormatTitleList')
  def getTargetFormatTitleList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[0], self.getTargetFormatItemList())

  security.declareProtected(Permissions.AccessContentsInformation, 'getTargetFormatList')
  def getTargetFormatList(self):
    """
      Returns a list of acceptable formats for conversion
    """
    return map(lambda x: x[1], self.getTargetFormatItemList())

  security.declareProtected(Permissions.ModifyPortalContent,'isTargetFormatAllowed')
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
      self.convertToBaseFormat()
    if format == 'text-content':
      # Extract text from the ODF file
      cs = cStringIO.StringIO()
      cs.write(_unpackData(self.getBaseData()))
      z = zipfile.ZipFile(cs)
      s = z.read('content.xml')
      s = self.rx_strip.sub(" ", s) # strip xml
      s = self.rx_compr.sub(" ", s) # compress multiple spaces
      cs.close()
      z.close()
      return 'text/plain', s
    server_proxy = self._mkProxy()
    response_code, response_dict, response_message = server_proxy.run_generate(self.getId(),
                                       enc(_unpackData(self.getBaseData())),
                                       None, 
                                       format)
    # XXX: handle possible OOOd server failure
    return response_dict['mime'], Pdata(dec(response_dict['data']))

  # Conversion API
  security.declareProtected(Permissions.View, 'convert')
  def convert(self, format, display=None, **kw):
    """
      Implementation of thGet file in a given format.
      Runs makeFile to make sure we have the requested version cached,
      then returns from cache.
    """
    # Make sure we can support html and pdf by default
    is_html = 0
    original_format = format
    if format == 'base-data':
      if not self.hasBaseData(): self.convertToBaseFormat()
      return self.getBaseContentType(), self.getBaseData()
    if format == 'pdf':
      format_list = [x for x in self.getTargetFormatList() if x.endswith('pdf')]
      format = format_list[0]
    elif format in STANDARD_IMAGE_FORMAT_LIST:
      format_list = [x for x in self.getTargetFormatList() if x.endswith(format)]
      format = format_list[0]
    elif format == 'html':
      format_list = [x for x in self.getTargetFormatList() if x.startswith('html')]
      format = format_list[0]
      is_html = 1
    elif format in ('txt', 'text', 'text-content'):
      format_list = self.getTargetFormatList()
      if format in format_list:
        format = format_list[format_list.index(format)]
      if 'txt' in format_list:
        format = format_list[format_list.index('txt')]
      elif 'text' in format_list:
        format = format_list[format_list.index('text')]
      else:
        return 'text/plain', self.asTextContent()
    # Raise an error if the format is not supported
    if not self.isTargetFormatAllowed(format):
      raise ConversionError("[DMS] Target format %s is not supported" % format)
    # Check if we have already a base conversion
    if not self.hasBaseData():
      self.convertToBaseFormat()
    # Return converted file
    if display is None or original_format not in STANDARD_IMAGE_FORMAT_LIST:
      has_format = self.hasConversion(format=format)
    else:
      has_format = self.hasConversion(format=format, display=display)
    if not has_format:
      # Do real conversion
      mime, data = self._convert(format)
      if is_html:
        # Extra processing required since
        # we receive a zip file
        cs = cStringIO.StringIO()
        cs.write(_unpackData(data))
        z = zipfile.ZipFile(cs)
        for f in z.infolist():
          fn = f.filename
          if fn.endswith('html'):
            data = z.read(fn)
            break
        mime = 'text/html'
        self.populateContent(zip_file=z)
        z.close()
        cs.close()
      if display is None or original_format not in STANDARD_IMAGE_FORMAT_LIST:
        self.setConversion(data, mime, format=format)
      else:
        temp_image = self.portal_contributions.newContent(
                                       portal_type='Image',
                                       temp_object=1)
        temp_image._setData(data)
        mime, data = temp_image.convert(format, display=display)
        self.setConversion(data, mime, format=format, display=display)
    if display is None or original_format not in STANDARD_IMAGE_FORMAT_LIST:
      return self.getConversion(format=format)
    else:
      return self.getConversion(format=format, display=display)

  security.declareProtected(Permissions.View, 'asTextContent')
  def asTextContent(self):
    """
      Extract plain text from ooo docs by stripping the XML file.
      This is the simplest way, the most universal and it is compatible
      will all formats.
    """
    return self._convert(format='text-content')

  security.declareProtected(Permissions.ModifyPortalContent, 'populateContent')
  def populateContent(self, zip_file=None):
    """
    Extract content from the ODF zip file and populate the document.
    Optional parameter zip_file prevents from converting content twice.
    """
    if zip_file is None:
      format_list = [x for x in self.getTargetFormatList() if x.startswith('html')]
      format = format_list[0]
      mime, data = self._convert(format)
      archive_file = cStringIO.StringIO()
      archive_file.write(_unpackData(data))
      zip_file = zipfile.ZipFile(archive_file)
      must_close = 1
    else:
      must_close = 0
    for f in zip_file.infolist():
      file_name = f.filename
      if not file_name.endswith('html'):
        document = self.get(file_name, None)
        if document is not None:
          self.manage_delObjects([file_name])
        self.portal_contributions.newContent(id=file_name, container=self,
                                             file_name=file_name,
                                             data=zip_file.read(file_name))
    if must_close:
      zip_file.close()
      archive_file.close()

  # Base format implementation
  security.declarePrivate('_convertToBaseFormat')
  def _convertToBaseFormat(self):
    """
      Converts the original document into ODF
      by invoking the conversion server. Store the result
      on the object. Update metadata information.
    """
    server_proxy = self._mkProxy()
    response_code, response_dict, response_message = server_proxy.run_convert(self.getSourceReference() or self.getId(),
                                      enc(_unpackData(self.getData())))
    if response_code == 200:
      # sucessfully converted document
      self._setBaseData(dec(response_dict['data']))
      metadata = response_dict['meta']
      self._base_metadata = metadata
      if metadata.get('MIMEType', None) is not None:
        self._setBaseContentType(metadata['MIMEType'])
    else:
      # log and raise errors with converting server.Explicitly raise the exception!
      LOG('[DMS]', ERROR, 'Error converting document to base format %s:%s' %(response_code, response_message))
      raise ConversionError("[DMS] Error converting document to base format %s:%s:"  
                                       %(response_code, response_message))

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
      Returns the metadata extracted by the conversion
      server.
    """
    return self._base_metadata

  security.declareProtected(Permissions.ModifyPortalContent, 'updateBaseMetadata')
  def updateBaseMetadata(self, *arg, **kw):
    """
      Updates metadata information in the converted OOo document
      based on the values provided by the user. This is implemented
      through the invocation of the conversion server.
    """
    server_proxy = self._mkProxy()
    response_code, response_dict, response_message = server_proxy.run_setmetadata(self.getId(),
                                                          enc(_unpackData(self.getBaseData())),
                                                          kw)
    if response_code == 200:
      # successful meta data extraction
      self._setBaseData(dec(response_dict['data']))
    else:
      # log and raise errors with converting server.Explicitly raise the exception!
      LOG('[DMS]', ERROR, "Error getting document's metadata %s:%s" %(response_code, response_message))
      raise ConversionError("[DMS] Error getting document's metadata %s:%s" %(response_code, response_message))
