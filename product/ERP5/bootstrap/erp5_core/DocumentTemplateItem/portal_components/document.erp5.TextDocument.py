# -*- coding: utf-8 -*-
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

from hashlib import md5
import six
from AccessControl.ZopeGuards import guarded_getattr
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from zLOG import LOG, WARNING
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.Document import Document, ConversionError, _MARKER, DEFAULT_CONTENT_TYPE
from erp5.component.document.File import File
from erp5.component.module.WebDAVSupport import TextContent
from erp5.component.document.Document import VALID_IMAGE_FORMAT_LIST, VALID_TEXT_FORMAT_LIST
from io import BytesIO
from string import Template

# Mixin Import
from erp5.component.mixin.CachedConvertableMixin import CachedConvertableMixin
from Products.ERP5Type.mixin.text_content_history import TextContentHistoryMixin
from Products.ERP5Type.Utils import bytes2str, str2bytes, str2unicode, unicode2str

from lxml import html as etree_html

class TextDocument(CachedConvertableMixin, TextContentHistoryMixin, TextContent, File):
  """
  A TextDocument implements IDocument, IFile, ICachedconvertable, ITextConvertable
  and ITextDocument.
  """

  meta_type = 'ERP5 Text Document'
  portal_type = 'Text Document'
  add_permission = Permissions.AddPortalContent

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.CategoryCore
                    , PropertySheet.DublinCore
                    , PropertySheet.Version
                    , PropertySheet.Document
                    , PropertySheet.ExternalDocument
                    , PropertySheet.Url
                    , PropertySheet.TextDocument
                    , PropertySheet.Data
                    , PropertySheet.Reference
                    )

  def _substituteTextContent(self, text, safe_substitute=True, **kw):
    # If a method for string substitutions of the text content, perform it.
    # Decode everything into unicode before the substitutions, in order to
    # avoid encoding errors.
    method_id = self.getTextContentSubstitutionMappingMethodId()
    if method_id:
      try:
        method = guarded_getattr(self, method_id)
      except AttributeError:
        LOG('TextDocument', WARNING, 'could not get the substitution'
            ' mapping method %s from %r, so the content will not be'
            ' substituted.' % (method_id, self.getRelativeUrl()))
        return text

      # unicode()
      is_str = isinstance(text, str)
      if six.PY2 and is_str:
        text = str2unicode(text)

      class LazyUnicodeMapping:
        """Lazily calls the substitution method if some substitution is needed
        and manage the str/unicode on py2.
        """
        _mapping = None
        @property
        def mapping(self):
          if self._mapping is None:
            self._mapping = method(**kw)
          return self._mapping

        def __getitem__(self, item):
          v = self.mapping[item]
          if six.PY2:
            if isinstance(v, str):
              v = str2unicode(v)
            elif not isinstance(v, six.text_type):
              v = str2unicode(str(v))
          else:
            if not isinstance(v, str):
              v = str(v)
          return v
      unicode_mapping = LazyUnicodeMapping()

      if safe_substitute:
        text = Template(text).safe_substitute(unicode_mapping)
      else:
        text = Template(text).substitute(unicode_mapping)

      # If the original was a str, convert it back from unicode() to str
      if six.PY2 and is_str:
        text = unicode2str(text)

    return text

  security.declareProtected(Permissions.AccessContentsInformation, 'asSubjectText')
  def asSubjectText(self, substitution_method_parameter_dict=None, safe_substitute=True, **kw):
    """
      Converts the subject of the document to a textual representation.
    """
    subject = TextDocument.inheritedAttribute('asSubjectText')(self, **kw)
    if substitution_method_parameter_dict is None:
      substitution_method_parameter_dict = {}
    return self._substituteTextContent(subject, safe_substitute=safe_substitute,
                                       **substitution_method_parameter_dict)

  def _convert(self, format, substitution_method_parameter_dict=None, # pylint: disable=redefined-builtin
              safe_substitute=True, charset=None, text_content=None, substitute=True, **kw):
    """
      Convert text using portal_transforms or oood
    """
    # `text_content` not renamed as parameter for backward compaptibility
    data = text_content
    if data is None:
      # `getData` first try to get data, then text content, but here we'd like the opposite
      data = self.getTextContent()
      if not data:
        data = self.getData()
    # XXX 'or DEFAULT_CONTENT_TYPE' is compaptibility code used for old
    # web_page that have neither content_type nor text_format. Migration
    # should be done to make all web page having content_type property
    src_mimetype = self.getContentType() or DEFAULT_CONTENT_TYPE
    if not format and src_mimetype == 'text/html':
      format = 'html' # Force safe_html
    if not format:
      # can return document without conversion
      return src_mimetype, data
    portal = self.getPortalObject()
    mime_type = portal.mimetypes_registry.lookupExtension('name.%s' % format)
    original_mime_type = mime_type = str(mime_type)
    if data:
      kw['format'] = format
      convert_kw = {}
      # PortalTransforms does not accept empty values for 'encoding' parameter
      if charset:
        kw['charset'] = convert_kw['encoding'] = charset
      if not self.hasConversion(**kw):
        portal_transforms = portal.portal_transforms
        filename = self.getFilename()
        if mime_type == 'text/html':
          mime_type = 'text/x-html-safe'
        if src_mimetype != "image/svg+xml":
          if not isinstance(data, bytes):
            data = str2bytes(data)
          result = portal_transforms.convertToData(mime_type, data,
                                                   object=self, context=self,
                                                   filename=filename,
                                                   mimetype=src_mimetype,
                                                   **convert_kw)
          if result is None:
            raise ConversionError('TextDocument conversion error. '
                                  'portal_transforms failed to convert '
                                  'from %r to %s: %r' %
                                  (src_mimetype, mime_type, self))
        else:
          result = data
        if format in VALID_IMAGE_FORMAT_LIST:
          # Include extra parameter for image conversions
          temp_image = self.portal_contributions.newContent(
                                       portal_type='Image',
                                       file=BytesIO(),
                                       filename=self.getId(),
                                       temp_object=1)
          if not isinstance(result, bytes):
            result = str2bytes(result)
          temp_image._setData(result)
          _, result = temp_image.convert(**kw)

        self.setConversion(result, original_mime_type, **kw)
      else:
        mime_type, result = self.getConversion(**kw)
      if format in VALID_TEXT_FORMAT_LIST:
        if six.PY3 and isinstance(result, bytes):
          result = bytes2str(result)
        if substitute:
          # only textual content can be sustituted
          if substitution_method_parameter_dict is None:
            substitution_method_parameter_dict = {}
          result = self._substituteTextContent(result, safe_substitute=safe_substitute,
                                               **substitution_method_parameter_dict)
      return original_mime_type, result
    else:
      # data is not set, return empty string instead of None
      return original_mime_type, ''

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentBaseURL')
  def getContentBaseURL(self):
    """
        Returns the content base URL based on the actual content
        (in HTML)
    """
    if self.hasTextContent():
      html = self._asHTML()
      # a document can be entirely stripped by safe_html
      # so its html conversion can be empty
      if html.strip():
        html_tree = etree_html.fromstring(html)
        base_list = [href for href in html_tree.xpath('//base/@href') if href]
        if base_list:
          return str(base_list[0])
    return Document.getContentBaseURL(self)

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentType')
  def getContentType(self, default=_MARKER): # pylint: disable=arguments-differ
    """Backward compatibility, read content_type
    from text_format property
    """
    if not self.hasContentType():
      # getProperty can not be used
      # because text_format is not registered in local_properties
      if default is _MARKER:
        return getattr(self, 'text_format', None)
      else:
        return getattr(self, 'text_format', default)
    else:
      if default is _MARKER:
        return self._baseGetContentType()
      else:
        return self._baseGetContentType(default)

  security.declareProtected(Permissions.AccessContentsInformation, 'isSupportTextConversion')
  def isSupportTextConversion(self):
    """
    Generally, a Text Document is convertable to text format.
    """
    return True

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextContent')
  def getTextContent(self, default=_MARKER):
    """
    Overridden method to check permission to access content in raw format.
    """
    self._checkConversionFormatPermission(None)
    return bytes2str(self.getData(default))

  security.declareProtected(Permissions.ModifyPortalContent, 'setTextContent')
  def setTextContent(self, text_content, **kw):
    """
    Setting text content is like setting data, but with a string argument.
    """
    self.setData(str2bytes(text_content), **kw)

  # Backward compatibility for replacement of text_format by content_type
  security.declareProtected(Permissions.AccessContentsInformation, 'getTextFormat')
  def getTextFormat(self, default=_MARKER):
    """
    """
    LOG('TextDocument', WARNING,
              'Usage of text_format is deprecated, use content_type instead')
    return self.getContentType(default)

  security.declareProtected(Permissions.ModifyPortalContent, 'setTextFormat')
  def setTextFormat(self, value):
    """
    """
    LOG('TextDocument', WARNING,
              'Usage of text_format is deprecated, use content_type instead')
    return self.setContentType(value)

  security.declareProtected(Permissions.ModifyPortalContent, '_setTextFormat')
  def _setTextFormat(self, value):
    """
    """
    LOG('TextDocument', WARNING,
              'Usage of text_format is deprecated, use content_type instead')
    return self._setContentType(value)

  def getData(self, default=_MARKER):
    # type: (bytes) -> bytes | PData
    """
    Goal: `getData` must returns original content.

    On a new instance, `data` will always hold original content, but for old
    instances, the original data could be stored in both `data`, or directly in
    `text_content`. The heuristic is to assume that `text_content` was always
    updated.
    """
    data = None

    try:
      text_content = aq_base(self).text_content or None
    except AttributeError:
      text_content = None

    # Opportunistic migration from `text_content` to `data`
    if text_content and self.hasData():
      data = str2bytes(text_content)
      if _checkPermission(Permissions.ModifyPortalContent, self):
        self.edit(
          data=data,
          notify_workflow=False,
        )
        del aq_base(self).text_content

    if not data and self.hasData():
      if default is _MARKER:
        data = File.getData(self)
      else:
        data = File.getData(self, default)

    return data

  security.declareProtected(Permissions.ModifyPortalContent, 'setData')
  def setData(self, value, **kw):
    """
    Handles taking care of the backward compatibility fix on `getData`:
    if data is first set, we need to erase text content without ever
    converting.
    """
    try:
      del aq_base(self).text_content
    except AttributeError:
      pass

    self._setData(value, **kw)

  def updateContentMd5(self):
    """Update md5 checksum from the original file

    Overriden here because CachedConvertableMixin version does not
    understand the dynamic nature TextDocument's data.
    """
    self._setContentMd5(md5(self.getData() or b'').hexdigest())
