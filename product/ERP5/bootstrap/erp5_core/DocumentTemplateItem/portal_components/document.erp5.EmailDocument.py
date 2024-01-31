# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Nexedi SA and Contributors. All Rights Reserved.
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

import re
import six
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.ERP5Type import Permissions, PropertySheet
from erp5.component.document.TextDocument import TextDocument
from erp5.component.document.File import File
from erp5.component.mixin.MailMessageMixin import MailMessageMixin, testCharsetAndConvert
from erp5.component.mixin.DocumentProxyMixin import DocumentProxyMixin, DocumentProxyError
from MethodObject import Method

try:
  from Products.MimetypesRegistry.interfaces import MimeTypeException # pylint: disable=unused-import
except ImportError:
  class MimeTypeException(Exception):
    """
    A dummy exception class which is used when MimetypesRegistry product is
    not installed yet.
    """

if six.PY2:
  from email import message_from_string as message_from_bytes
else:
  from email import message_from_bytes

from email.utils import parsedate_tz, mktime_tz

DEFAULT_TEXT_FORMAT = 'text/html'
COMMASPACE = ', '
_MARKER = object()

filename_regexp = 'name="([^"]*)"'


class EmailDocumentProxyMixin(DocumentProxyMixin):
  """
  Provides access to documents referenced by the causality field
  """
  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  security.declareProtected(Permissions.AccessContentsInformation, 'hasFile')
  def hasFile(self):
    """
    hasFile is used in many parts of EmailDocument in order to know
    if there is some document content to manage. We define it here
    in order to say that there is no document if we are not able to
    get the proxy
    """
    has_file = False
    try:
      proxied_document = self.getProxiedDocument()
      has_file = proxied_document.hasFile()
    except DocumentProxyError:
      pass
    return has_file

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextContent')
  def getTextContent(self, default=_MARKER):
    result = None
    try:
      proxied_document = self.getProxiedDocument()
      result = proxied_document.getTextContent(default=default)
    except DocumentProxyError:
      pass
    if default is _MARKER:
      return result
    return result or default

class ProxiedMethod(Method):
  """
  Accessort that retrieve methods directly on the proxy
  """

  def __init__(self, proxied_method_id):
    self.proxied_method_id = proxied_method_id

  def __call__(self, instance, *args, **kw):
    proxied_document = instance.getProxiedDocument()
    method = getattr(proxied_document, self.proxied_method_id)
    return method(*args, **kw)

# generate all proxy method on EmailDocumentProxyMixin
for method_id in ('getContentType',
                  'getContentInformation', 'getAttachmentData',
                  'getAttachmentInformationList'):
  EmailDocumentProxyMixin.security.declareProtected(
       Permissions.AccessContentsInformation,
       method_id)
  setattr(EmailDocumentProxyMixin, method_id,
      ProxiedMethod(method_id))

class EmailDocument(TextDocument, MailMessageMixin):
  """
    EmailDocument is a File which stores its metadata in a form which
    is similar to a TextDocument.
    A Text Document which stores raw HTML and can
    convert it to various formats.
  """

  meta_type = 'ERP5 Email Document'
  portal_type = 'Email Document'
  add_permission = Permissions.AddPortalContent
  # XXX must be removed later - only event is a delivery
  isDelivery = ConstantGetter('isDelivery', value=True)

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
                    , PropertySheet.Arrow
                    , PropertySheet.Task
                    , PropertySheet.ItemAggregation
                    , PropertySheet.EmailHeader
                    , PropertySheet.Reference
                    , PropertySheet.Data
                    )

  # Mail processing API
  def _getMessage(self):
    # Email Document is not a representation of SMTP payload, thus we no longer
    # store it in 'data' property.
    result = getattr(self, '_v_message', None)
    if result is None:
      data = bytes(self.getData() or b'')
      if not data:
        # Generated a mail message temporarily to provide backward compatibility.
        document_type_list = list(self.getPortalEmbeddedDocumentTypeList()) + list(self.getPortalDocumentTypeList())
        data = self.Base_createMailMessageAsString(
          from_url='from@example.com',
          to_url='to@example.com',
          subject=self.getTitle() or '',
          body=self.getTextContent() or '',
          content_type=self.getContentType(),
          embedded_file_list=self.getAggregateValueList(portal_type=document_type_list),
        )
        if six.PY3:
          data = data.encode()
      result = message_from_bytes(data)
      self._v_message = result
    return result

  def _setData(self, data):
    super(EmailDocument, self)._setData(data)
    try:
      del self._v_message
    except AttributeError:
      pass

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSupportBaseDataConversion')
  def isSupportBaseDataConversion(self):
    """
    """
    return False

  # Overriden methods
  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
  def getTitle(self, default=_MARKER):
    """
    Returns the title from the mail subject
    """
    if not self.hasFile():
      # Return the standard text content if no file was provided
      if default is _MARKER:
        return self._baseGetTitle()
      else:
        return self._baseGetTitle(default)
    subject = self.getContentInformation().get('Subject', '')
    # Remove all newlines
    subject = subject.replace('\r', '')
    subject = subject.replace('\n', '')
    return subject

  security.declareProtected(Permissions.AccessContentsInformation, 'getStartDate')
  def getStartDate(self, default=_MARKER):
    """
    Returns the date from the mail date
    """
    if not self.hasFile():
      # Return the standard start date if no file was provided
      if default is _MARKER:
        return self._baseGetStartDate()
      else:
        return self._baseGetStartDate(default)
    date_string = self.getContentInformation().get('Date', None)
    if date_string:
      parsed_date_string = parsedate_tz(date_string)
      if parsed_date_string is not None:
        time = mktime_tz(parsed_date_string)
        if time:
          return DateTime(time)
    return self.getCreationDate()

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextContent')
  def getTextContent(self, default=_MARKER):
    """
    Returns the content of the email as text. This is useful
    to display the content of an email.
    """
    self._checkConversionFormatPermission(None)
    if not self.hasFile():
      # Return the standard text content if no file was provided
      # Or standard text content is not empty.
      if default is _MARKER:
        return self._baseGetTextContent()
      else:
        return self._baseGetTextContent(default)

    else:
      part = self._getMessageTextPart()
      if part is None:
        text_result = ""
      else:
        part_encoding = part.get_content_charset()
        message_text = part.get_payload(decode=1)
        text_result, _ = testCharsetAndConvert(message_text,
                                                      part.get_content_type(),
                                                      part_encoding)
        if part.get_content_type() == 'text/html':
          _, text_result = self.convert(format='html',
                                           text_content=text_result,
                                           charset=part_encoding)

    if default is _MARKER:
      return text_result
    return text_result or default

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentType')
  def getContentType(self, default=_MARKER):
    """
    Returns the format of the email (text or html).

    TODO: add support for legacy objects
    """
    if not self.hasFile():
      # Return the standard text format if no file was provided
      if default is _MARKER:
        return TextDocument.getContentType(self)
      else:
        return TextDocument.getContentType(self, default)
    else:
      part = self._getMessageTextPart()
      if part is None:
        return 'text/plain'
      else:
        return part.get_content_type()

  email_parser = re.compile(r'[ ;,<>\'"]*([^<> ;,\'"]+?\@[^<> ;,\'"]+)[ ;,<>\'"]*', re.IGNORECASE)
  security.declareProtected(Permissions.AccessContentsInformation, 'getContentURLList')
  def getContentURLList(self):
    """
      Overriden to include emails as URLs
    """
    result = TextDocument.getContentURLList(self)
    result.extend(re.findall(self.email_parser, self.getSender('')))
    result.extend(re.findall(self.email_parser, self.getRecipient('')))
    result.extend(re.findall(self.email_parser, self.getCcRecipient('')))
    result.extend(re.findall(self.email_parser, self.getBccRecipient('')))
    return result

  # Conversion API Implementation
  def _convertToBaseFormat(self):
    """
      Build a structure which can be later used
      to extract content information from this mail
      message.
    """
    pass

  security.declareProtected(Permissions.View, 'index_html')
  index_html = TextDocument.index_html

  security.declareProtected(Permissions.AccessContentsInformation, 'convert')
  convert = TextDocument.convert

  security.declareProtected(Permissions.AccessContentsInformation, 'hasBaseData')
  def hasBaseData(self):
    """
      Since there is no need to convert to a base format, we consider that
      we always have the base format data if and only is we have
      some text defined or a file.
    """
    return self.hasFile() or self.hasTextContent()

  # Methods which can be useful to prepare a reply by email to an event
  security.declareProtected(Permissions.AccessContentsInformation, 'getReplyBody')
  def getReplyBody(self, content_type=None):
    """This is used in order to respond to a mail, this put a '> ' before each
    line of the body.
    """
    if not content_type:
      content_type = self.getContentType()
    if content_type == 'text/plain':
      body = self.asText()
      if body:
        return '> ' + str(body).replace('\n', '\n> ')
    elif content_type == 'text/html':
      # XXX we add some empty <p> to be able to enter text before the quoted
      # content in CKEditor.
      return '''<p>&nbsp;</p><blockquote type="cite">
%s
</blockquote><p>&nbsp;</p>''' % self.asStrippedHTML()
    return ''

  security.declareProtected(Permissions.AccessContentsInformation, 'getReplySubject')
  def getReplySubject(self):
    """
      This is used in order to respond to a mail,
      this put a 'Re: ' before the orignal subject

      XXX - not multilingual
    """
    reply_subject = self.getTitle()
    if reply_subject.find('Re: ') != 0:
      reply_subject = 'Re: ' + reply_subject
    return reply_subject

  security.declareProtected(Permissions.AccessContentsInformation, 'getReplyTo')
  def getReplyTo(self):
    """
      Returns the send of this message based on getContentInformation
    """
    content_information = self.getContentInformation()
    return content_information.get('Return-Path', content_information.get('From'))

  security.declareProtected(Permissions.UseMailhostServices, 'sendMailHostMessage')
  def sendMailHostMessage(self, message):
    """
      Send one by one

      XXX - Needs to be unified with Event methods
    """
    self.MailHost.send(message)

  # Because TextDocument is base_convertable and not EmailDocument.
  # getData must be implemented like File.getData is.
  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  getData = File.getData
  getContentInformation = MailMessageMixin.getContentInformation
