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

import re, types
from DateTime import DateTime
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.ERP5Type.Accessor.Constant import PropertyGetter as ConstantGetter
from Products.CMFCore.utils import _checkPermission
from Products.ERP5Type import Permissions, PropertySheet
from Products.ERP5.Document.TextDocument import TextDocument
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import ConversionError
from Products.ERP5.mixin.document_proxy import DocumentProxyMixin, DocumentProxyError
from Products.ERP5.Tool.NotificationTool import buildEmailMessage
from Products.ERP5Type.Utils import guessEncodingFromText
from MethodObject import Method
from zLOG import LOG, INFO

try:
  from Products.MimetypesRegistry.common import MimeTypeException
except ImportError:
  class MimeTypeException(Exception):
    """
    A dummy exception class which is used when MimetypesRegistry product is
    not installed yet.
    """

from email import message_from_string
from email.Header import decode_header, HeaderParseError
from email.Utils import parsedate_tz, mktime_tz

DEFAULT_TEXT_FORMAT = 'text/html'
COMMASPACE = ', '
_MARKER = []

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
  Accessor that retrieves methods directly on the proxy
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

class EmailDocument(TextDocument):
  """
    EmailDocument is a File which stores its metadata in a form which
    is similar to a TextDocument.
    A Text Document which stores raw HTML and can 
    convert it to various formats.

    one more line for testing
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
    result = getattr(self, '_v_message', None)
    if result is None:
      result = message_from_string(str(self.getData()))
      self._v_message = result
    return result

  def _getMessageTextPart(self):
    """
    Return the main text part of the message data

    Based on rfc: http://tools.ietf.org/html/rfc2046#section-5.1.4)
    """
    # Default value if no text is found
    found_part = None

    part_list = [self._getMessage()]
    while part_list:
      part = part_list.pop(0)
      if part.is_multipart():
        if part.get_content_subtype() == 'alternative':
          # Try to get the favourite text format defined on preference
          preferred_content_type = self.getPortalObject().portal_preferences.\
                                         getPreferredTextFormat('text/html')
          favourite_part = None
          for subpart in part.get_payload():
            if subpart.get_content_type() == preferred_content_type:
              part_list.insert(0, subpart)
            else:
              part_list.append(subpart)
        else:
          part_list.extend(part.get_payload())
      elif part.get_content_maintype() == 'text':
        found_part = part
        break

    return found_part

  security.declareProtected(Permissions.AccessContentsInformation,
                            'isSupportBaseDataConversion')
  def isSupportBaseDataConversion(self):
    """
    """
    return False

  security.declareProtected(Permissions.AccessContentsInformation, 'getContentInformation')
  def getContentInformation(self):
    """
    Returns the content information from the header information.
    This is used by the metadata discovery system.

    Header information is converted in UTF-8 since this is the standard
    way of representing strings in ERP5.
    """
    result = {}
    for (name, value) in self._getMessage().items():
      try: 
        decoded_header = decode_header(value)
      except HeaderParseError, error_message:
        decoded_header = ()
        LOG('EmailDocument.getContentInformation', INFO,
            'Failed to decode %s header of %s with error: %s' %
            (name, self.getPath(), error_message))
      for text, encoding in decoded_header:
        try:
          if encoding is not None:
            text = text.decode(encoding).encode('utf-8')
          else:
            text = text.decode().encode('utf-8')
        except (UnicodeDecodeError, LookupError), error_message:
          encoding = guessEncodingFromText(text, content_type='text/plain')
          if encoding is not None:
            try:
              text = text.decode(encoding).encode('utf-8')
            except (UnicodeDecodeError, LookupError), error_message:
              text = repr(text)[1:-1]
          else:
            text = repr(text)[1:-1]
        if name in result:
          result[name] = '%s %s' % (result[name], text)
        else:
          result[name] = text
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAttachmentInformationList')
  def getAttachmentInformationList(self, **kw):
    """
    Returns a list of dictionnaries for every attachment. Each dictionnary
    represents the metadata of the attachment.
    **kw - support for listbox (TODO: improve it)
    """
    result = []
    for i, part in enumerate(self._getMessage().walk()):
      if not part.is_multipart():
        kw = dict(part.items())
        kw['uid'] = 'part_%s' % i
        kw['index'] = i
        filename = part.get_filename()
        if not filename:
          # get_filename return name only from Content-Disposition header
          # of the message but sometimes this value is stored in
          # Content-Type header
          content_type_header = kw.get('Content-Type',
                                                    kw.get('Content-type', ''))
          filename_list = re.findall(filename_regexp,
                                      content_type_header,
                                      re.MULTILINE)
          if filename_list:
            filename = filename_list[0]
        if filename:
          kw['filename'] = filename
        else:
          content_disposition = kw.get('Content-Disposition', 
                                           kw.get('Content-disposition', None))
          prefix = 'part_'
          if content_disposition:
            if content_disposition.split(';')[0] == 'attachment':
              prefix = 'attachment_'
            elif content_disposition.split(';')[0] == 'inline':
              prefix = 'inline_'
          kw['filename'] = '%s%s' % (prefix, i)
        kw['content_type'] = part.get_content_type()
        result.append(kw)
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAttachmentData')
  def getAttachmentData(self, index, REQUEST=None):
    """
    Returns the decoded data of an attachment.
    """
    for i, part in enumerate(self._getMessage().walk()):
      if index == i:
        # This part should be handled in skin script
        # but it was a bit easier to access items here
        kw = dict(part.items())
        content_type = part.get_content_type()
        if REQUEST is not None:
          filename = part.get_filename()
          if not filename:
            # get_filename return name only from Content-Disposition header
            # of the message but sometimes this value is stored in
            # Content-Type header
            content_type_header = kw.get('Content-Type',
                                                    kw.get('Content-type', ''))
            filename_list = re.findall(filename_regexp,
                                        content_type_header,
                                        re.MULTILINE)
            if filename_list:
              filename = filename_list[0]
          RESPONSE = REQUEST.RESPONSE
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          if content_type and filename:
            RESPONSE.setHeader('Content-Type', content_type)
            RESPONSE.setHeader('Content-disposition',
                               'attachment; filename="%s"' % filename.encode('utf-8'))
#                               'attachment; filename="%s"' % filename)
        if 'text/html' in content_type:
          # Strip out html content in safe mode.
          mime, content = self.convert(format='html',
                                       text_content=part.get_payload(decode=1),
                                       index=index) # add index to generate
                                       # a unique cache key per attachment
        else:
          content = part.get_payload(decode=1)
        return content
    return KeyError, "No attachment with index %s" % index

  # Helper methods which override header property sheet
  security.declareProtected(Permissions.AccessContentsInformation, 'getSender')
  def getSender(self, *args):
    """
    """
    if not self.hasData():
      return self._baseGetSender(*args)
    return self.getContentInformation().get('From', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getRecipient')
  def getRecipient(self, *args):
    """
    """
    if not self.hasData():
      return self._baseGetRecipient(*args)
    return self.getContentInformation().get('To', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getCcRecipient')
  def getCcRecipient(self, *args):
    """
    """
    if not self.hasData():
      return self._baseGetCcRecipient(*args)
    return self.getContentInformation().get('Cc', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getGroupingReference')
  def getGroupingReference(self, *args):
    """
      The reference refers here to the Thread of messages.
    """
    if not self.hasData():
      result = self._baseGetGroupingReference(*args)
    else:
      if not len(args):
        args = (self._baseGetGroupingReference(),)
      result = self.getContentInformation().get('References', *args)
      if result:
        result = result.split() # Only take the first reference
        if result:
          result = result[0]
    if result:
      return result
    return self.getFilename(*args)

  security.declareProtected(Permissions.AccessContentsInformation,
                            'getSourceReference')
  def getSourceReference(self, *args):
    """
      The Message-ID is considered here as the source reference
      of the message on the sender side (source)
    """
    if not self.hasData():
      return self._baseGetSourceReference(*args)
    if not len(args):
      args = (self._baseGetSourceReference(),)
    content_information = self.getContentInformation()
    return content_information.get('Message-ID') or content_information.get('Message-Id', *args)

  security.declareProtected(Permissions.AccessContentsInformation, 'getDestinationReference')
  def getDestinationReference(self, *args):
    """
      The In-Reply-To is considered here as the reference
      of the thread on the side of a former sender (destination)

      This is a hack which can be acceptable since 
      the reference of an email is shared.
    """
    if not self.hasData():
      return self._baseGetDestinationReference(*args)
    if not len(args):
      args = (self._baseGetDestinationReference(),)
    return self.getContentInformation().get('In-Reply-To', *args)

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
        try:
          try:
            time = mktime_tz(parsed_date_string)
          except OverflowError: # No way to get a date - parsing failed (XXX)
            time = None		  
	  if time:
	    return DateTime(time)
        except ValueError:
	  # If the parsed date is not conformant, nothing to do
          pass
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
        if part.get_content_type() == 'text/html':
          mime, text_result = self.convert(format='html',
                                           text_content=message_text,
                                           charset=part_encoding)
        else:
          if part_encoding != 'utf-8':
            try:
              if part_encoding is not None:
                text_result = message_text.decode(part_encoding).encode('utf-8')
              else:
                text_result = message_text.decode().encode('utf-8')
            except (UnicodeDecodeError, LookupError), error_message:
              LOG('EmailDocument.getTextContent', INFO, 
                  'Failed to decode %s TEXT message of %s with error: %s' % 
                  (part_encoding, self.getPath(), error_message))
              codec = guessEncodingFromText(message_text,
                                            content_type=part.get_content_type())
              if codec is not None:
                try:
                  text_result = message_text.decode(codec).encode('utf-8')
                except (UnicodeDecodeError, LookupError):
                  text_result = repr(message_text)
              else:
                text_result = repr(message_text)
          else:
            text_result = message_text

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

  email_parser = re.compile('[ ;,<>\'"]*([^<> ;,\'"]+?\@[^<> ;,\'"]+)[ ;,<>\'"]*',re.IGNORECASE)
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
  def getReplyBody(self):
    """
      This is used in order to respond to a mail,
      this put a '> ' before each line of the body
    """
    if self.getContentType() == 'text/plain':
      body = self.asText()
      if body:
        return '> ' + str(body).replace('\n', '\n> ')
    elif self.getContentType() == 'text/html':
      return '<br/><blockquote type="cite">\n%s\n</blockquote>' %\
                                self.asStrippedHTML()
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

  security.declareProtected(Permissions.UseMailhostServices, 'send')
  def send(self, from_url=None, to_url=None, cc_url=None, bcc_url=None, reply_url=None, subject=None,
           body=None, attachment_format=None, attachment_list=None, download=False):
    """
      Sends the current event content by email. If documents are
      attached through the aggregate category, enclose them.

      XXX - needs to be unified with Event methods

      from_url - the sender of this email. If not provided
                 we will use source to find a valid
                 email address

      to_url   - the recipients of this email. If not provided
                 we will use destination category to 
                 find a list of valid email addresses

      reply_url - the email address to reply to. If nothing
                 is provided, use the email defined in 
                 preferences.

      subject  - a custom title. If not provided, we will use
                 getTitle

      body     - a body message If not provided, we will
                 use the text representation of the event
                 as body (UTF-8)

      attachment_list -- list of dictionary which contains raw data and
                         name and mimetype for attachment.
                         See NotificationTool.buildEmailMessage.

      attachment_format - defines an option format
                 to convet attachments to (ex. application/pdf)

      download - if set to True returns, the message online
                rather than sending it.

      TODO: support conversion to base format and use
      base format rather than original format

      TODO2: consider turning this method into a general method for
      any ERP5 document.
    """
    if not _checkPermission(Permissions.View, self):
      raise Unauthorized

    additional_headers = {}

    #
    # Build mail message
    # This part will be replaced with MailTemplate soon.
    #
    if body is None:
      body = self.asText()

    # Subject
    if subject is None:
      subject = self.getTitle()

    # From
    if from_url is None:
      sender = self.getSourceValue()
      if sender is not None:
        if sender.getTitle():
          from_url = '"%s" <%s>' % (sender.getTitle(),
                                  sender.getDefaultEmailText())
        else:
          from_url = sender.getDefaultEmailText()
      elif self.getSender():
        from_url = self.getSender() # Access sender directly

    # Return-Path
    if reply_url is None:
      reply_url = self.portal_preferences.getPreferredEventSenderEmail()
    if reply_url:
      additional_headers['Return-Path'] = reply_url

    # Reply-To
    destination_reference = self.getDestinationReference()
    if destination_reference is not None:
      additional_headers['In-Reply-To'] = destination_reference

    # To (multiple)
    to_url_list = []
    if to_url is None:
      for recipient in self.getDestinationValueList():
        email = recipient.getDefaultEmailText()
        if email:
          if recipient.getTitle():
            to_url_list.append('"%s" <%s>' % (recipient.getTitle(), email))
          else:
            to_url_list.append(email)
        else:
          raise ValueError, 'Recipient %s has no defined email' % recipient
      if not to_url_list and self.getRecipient():
        to_url_list.append(self.getRecipient())
    elif type(to_url) in types.StringTypes:
      to_url_list.append(to_url)

    # bcc_url
    if bcc_url is None:
      bcc_url = self.getBccRecipient()
    if cc_url is None:
      cc_url = self.getCcRecipient()

    # Attachments
    if attachment_list is None:
      attachment_list = []
    document_type_list = self.getPortalDocumentTypeList()
    for attachment in self.getAggregateValueList():
      mime_type = None
      content = None
      name = None
      if not attachment.getPortalType() in document_type_list:
        mime_type = 'application/pdf'
        content = attachment.asPDF() # XXX - Not implemented yet
      else:
        #
        # Document type attachment
        #

        # WARNING - this could fail since getContentType
        # is not (yet) part of Document API
        if getattr(attachment, 'getContentType', None) is not None:
          mime_type = attachment.getContentType()
        else:
          raise ValueError, "Cannot find mimetype of the document."

        if mime_type is not None:
          try:
            mime_type, content = attachment.convert(mime_type)
            if mime_type is None: mime_type = 'application/pdf' # dirty hack JPS
          except ConversionError:
            mime_type = attachment.getBaseContentType()
            if mime_type is None: mime_type = 'application/pdf' # dirty hack JPS
            content = attachment.getBaseData()
          except (NotImplementedError, MimeTypeException):
            pass

        if content is None:
          if getattr(attachment, 'getTextContent', None) is not None:
            content = attachment.getTextContent()
          elif getattr(attachment, 'getData', None) is not None:
            content = attachment.getData()
          elif getattr(attachment, 'getBaseData', None) is not None:
            content = attachment.getBaseData()

      if not isinstance(content, str):
        content = str(content)

      attachment_list.append({'mime_type':mime_type,
                              'content':content,
			      'name':attachment.getReference() or attachment.getTitle() or attachment.Id()}
                             )

    mail_message = None
    for to_url in to_url_list:
      mime_message = buildEmailMessage(from_url=from_url, to_url=to_url, # XXX Missing Cc
                                       cc_url=cc_url, bcc_url=bcc_url,
                                       msg=body, subject=subject,
                                       attachment_list=attachment_list,
                                       additional_headers=additional_headers)
      mail_message = mime_message.as_string()
      self.activate(activity='SQLQueue').sendMailHostMessage(mail_message)

    # Save one of mail messages.
    if mail_message is not None:
      self.setData(mail_message)

    # Only for debugging purpose
    if download:
      return mail_message

  security.declareProtected(Permissions.UseMailhostServices, 'sendMailHostMessage')
  def sendMailHostMessage(self, message):
    """
      Send one by one

      XXX - Needs to be unified with Event methods
    """
    self.MailHost.send(message) # uggly hardcoding

  # Because TextDocument is base_convertable and not EmailDocument.
  # getData must be implemented like File.getData is.
  security.declareProtected(Permissions.AccessContentsInformation, 'getData')
  getData = File.getData
