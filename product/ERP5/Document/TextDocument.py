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

from AccessControl.ZopeGuards import guarded_getattr
from AccessControl import ClassSecurityInfo
from zLOG import LOG, WARNING
from Products.ERP5Type.Base import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _setCacheHeaders, _ViewEmulator
from Products.ERP5Type import Permissions, PropertySheet, Constraint, interfaces
from Products.ERP5.Document.Document import Document, ConversionError
from Products.ERP5Type.WebDAVSupport import TextContent
from Products.CMFDefault.utils import isHTMLSafe
import re

try:
  from string import Template
except ImportError:
  from Products.ERP5Type.patches.string import Template

DEFAULT_TEXT_FORMAT = 'text/html'

class TextDocument(Document, TextContent):
    """
        A Document contains text which can be formatted using
        *Structured Text* or *HTML*. Text can be automatically translated
        through the use of 'message catalogs'.

        Document inherits from XMLObject and can
        be synchronized accross multiple sites.

        Version Management: the notion of version depends on the
        type of application. For example, in the case (1) of Transformation
        (BOM), all versions are considered as equal and may be kept
        indefinitely for both archive and usage purpose. In the case (2)
        of Person data, the new version replaces the previous one
        in place and is not needed for archive. In the case (3) of
        a web page, the new version replaces the previous one,
        the previous one being kept in place for archive.

        Subcontent: documents may include subcontent (files, images, etc.)
        so that publication of rich content can be path independent.
    """

    meta_type = 'ERP5 Text Document'
    portal_type = 'Text Document'
    add_permission = Permissions.AddPortalContent
    isPortalContent = 1
    isRADContent = 1
    isDocument = 1

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
                      , PropertySheet.Snapshot
                      , PropertySheet.ExternalDocument
                      , PropertySheet.Url
                      , PropertySheet.TextDocument
                      )

    # Explicit inheritance
    security.declareProtected(Permissions.ModifyPortalContent, 'PUT')
    PUT = TextContent.PUT # We have a security issue here with Zope < 2.8

    security.declareProtected(Permissions.View, 'manage_FTPget')
    manage_FTPget = TextContent.manage_FTPget

    # File handling
    security.declarePrivate( '_edit' )
    def _edit(self, **kw):
      """\
        This is used to edit files which contain HTML content.
      """
      if kw.has_key('file'):
        file = kw.get('file')
        text_content = file.read()
        headers, body, format = self.handleText(text=text_content)
        kw.setdefault('text_format', format)
        kw.setdefault('text_content', text_content)
        del kw['file']
      # The following has been commented because a TextDocument
      # instance may contain something else than HTML
      ## Check if it's safe to save HTML content
      ## By default FCKEditor used to edit Web Pages wouldn't allow inserting
      ## HTML tags (will replace them accordingly) so this is the last possible 
      ## step where we can check if any other scripts wouldn't try to set manually
      ## bad HTML content.
      # if isHTMLSafe(kw.get('text_content', '')):
      #  Document._edit(self, **kw)
      # else:
      #  raise ValueError, "HTML contains illegal tags."
      Document._edit(self, **kw)

    security.declareProtected( Permissions.ModifyPortalContent, 'edit' )
    edit = WorkflowMethod( _edit )

    # Default Display
    security.declareProtected(Permissions.View, 'index_html')
    def index_html(self, REQUEST, RESPONSE, format=None, **kw):
      """
        Unlike for images and files, we want to provide
        in the case of HTML a nice standard display with
        all the layout of a Web Site. If no format is provided,
        the default rendering will use the standard ERP5 machinery.
        By providing a format parameter, it is possible to
        convert the text content into various formats.
      """
      if format is None:
        # The default is to use ERP5 Forms to render the page
        return self.view()
      mime, data = self.convert(format=format) 
      RESPONSE.setHeader('Content-Length', len(str(data))) # XXX - Not efficient 
                                                           # if datastream instance
      RESPONSE.setHeader('Content-Type', mime)
      RESPONSE.setHeader('Accept-Ranges', 'bytes')
      return data

    def _substituteTextContent(self, text, **kw):
      # If a method for string substitutions of the text content, perform it.
      # Decode everything into unicode before the substitutions, in order to
      # avoid encoding errors.
      method_id = self.getTextContentSubstitutionMappingMethodId()
      if method_id:
        try:
          mapping = guarded_getattr(self, method_id)(**kw)
        except AttributeError:
          LOG('TextDocument', WARNING, 'could not get the substitution mapping method %s from %r, so the content will not be substituted.' % (method_id, self))
          return text

        is_str = isinstance(text, str)
        if is_str:
          text = text.decode('utf-8')

        unicode_mapping = {}
        for k, v in mapping.iteritems():
          if isinstance(v, str):
            v = v.decode('utf-8')
          elif not isinstance(v, unicode):
            v = str(v).decode('utf-8')
          unicode_mapping[k] = v

        text = Template(text).substitute(unicode_mapping)

        # If the original was a str, convert it back to str.
        if is_str:
          text = text.encode('utf-8')

      return text

    security.declareProtected(Permissions.View, 'asSubjectText')
    def asSubjectText(self, substitution_method_parameter_dict=None, **kw):
      """
        Converts the subject of the document to a textual representation.
      """
      subject = TextDocument.inheritedAttribute('asSubjectText')(self, **kw)
      if substitution_method_parameter_dict is None:
        substitution_method_parameter_dict = {}
      return self._substituteTextContent(subject, **substitution_method_parameter_dict)

    security.declareProtected(Permissions.View, 'convert')
    def convert(self, format, substitution_method_parameter_dict=None, **kw):
      """
        Convert text using portal_transforms or oood
      """
      # Accelerate rendering in Web mode
      _setCacheHeaders(_ViewEmulator().__of__(self), {'format' : format})
      # Return the raw content
      if format == 'raw':
        return 'text/plain', self.getTextContent()
      mime_type = getToolByName(self, 'mimetypes_registry').lookupExtension('name.%s' % format)
      mime_type = str(mime_type)
      src_mimetype = self.getTextFormat(DEFAULT_TEXT_FORMAT)
      if not src_mimetype.startswith('text/'):
        src_mimetype = 'text/%s' % src_mimetype
      # check if document has set text_content and convert if necessary
      text_content = self.getTextContent()
      if text_content:
        if not self.hasConversion(format=format):
          portal_transforms = getToolByName(self, 'portal_transforms')
          result = portal_transforms.convertToData(mime_type, text_content,
                                                   object=self, context=self,
                                                   filename=self.getTitleOrId(),
                                                   mimetype=src_mimetype)
          if result is None:
            raise ConversionError('TextDocument conversion error. '
                                  'portal_transforms failed to convert to %s: %r' % (mime_type, self))
          self.setConversion(result, mime_type, format=format)
        else:
          mime_type, result = self.getConversion(format=format)
        if substitution_method_parameter_dict is None:
          substitution_method_parameter_dict = {}
        result = self._substituteTextContent(result, **substitution_method_parameter_dict)
        return mime_type, result
      else:
        # text_content is not set, return empty string instead of None
        return mime_type, ''

    def __call__(self):
      _setCacheHeaders(_ViewEmulator().__of__(self), {})
      return Document.__call__(self)

    security.declareProtected(Permissions.AccessContentsInformation, 'getContentBaseURL')
    def getContentBaseURL(self):
      """
        Returns the content base URL based on the actual content
        (in HTML)
      """
      if self.hasBaseData():
        html = self._asHTML()
        base_list = re.findall(self.base_parser, str(html))
        if base_list:
          return base_list[0]
      return Document.getContentBaseURL(self)

    security.declareProtected(Permissions.AccessContentsInformation, 'hasBaseData')
    def hasBaseData(self):
      """
        A TextDocument store its data in the "text_content" property. Since
        there is no such thing as base_data in TextDocument, having base_data
        is equivalent to having some text_content.
      """
      return self.hasTextContent()

    security.declareProtected(Permissions.AccessContentsInformation, 'getMimeTypeAndContent')
    def getMimeTypeAndContent(self):
      """This method returns a tuple which contains mimetype and content."""
      return (self.getTextFormat(), self.getTextContent())
