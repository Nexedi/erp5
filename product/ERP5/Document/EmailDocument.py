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
from Globals import get_request
from AccessControl import ClassSecurityInfo, Unauthorized
from Products.ERP5Type.Base import WorkflowMethod
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore.utils import _setCacheHeaders, _ViewEmulator
from Products.CMFDefault.utils import isHTMLSafe
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.TextDocument import TextDocument
from Products.ERP5.Document.File import File
from Products.ERP5.Document.Document import ConversionError
from Products.ERP5.Tool.NotificationTool import buildEmailMessage

try:
  from Products.MimetypesRegistry.common import MimeTypeException
except ImportError:
  class MimeTypeException(Exception):
    """
    A dummy exception class which is used when MimetypesRegistry product is
    not installed yet.
    """
try:
  import libxml2
  import libxslt
  import_libxml2 = 1
except ImportError:
  import_libxml2 = 0

from email import message_from_string
from email.Header import decode_header
from email.Utils import parsedate_tz, mktime_tz

DEFAULT_TEXT_FORMAT = 'text/html'
COMMASPACE = ', '
_MARKER = []

file_name_regexp = 'name="([^"]*)"'

class EmailDocument(File, TextDocument):
  """
    EmailDocument is a File which stores its metadata in a form which
    is similar to a TextDocument.
    A Text Document which stores raw HTML and can 
    convert it to various formats.
  """

  meta_type = 'ERP5 Email Document'
  portal_type = 'Email Document'
  add_permission = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent = 1
  isDocument = 1
  isDelivery = 1 # XXX must be removed later - only event is a delivery

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
                    , PropertySheet.Arrow
                    , PropertySheet.Task
                    , PropertySheet.ItemAggregation
                    )

  # Declarative interfaces
  __implements__ = ()

  # Searchable Text - at least search the body message
  #                 - later: search attachments too
  searchable_property_list = TextDocument.searchable_property_list

  # Mail processing API
  def _getMessage(self):
    result = getattr(self, '_v_message', None)
    if result is None:
      result = message_from_string(str(self.getData()))
      self._v_message = result
    return result

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
      for text, encoding in decode_header(value):
        if encoding is not None:
          text = text.decode(encoding).encode('utf-8')
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
    i = 0
    for part in self._getMessage().walk():
      if not part.is_multipart():
        kw = dict(part.items())
        kw['uid'] = 'part_%s' % i
        kw['index'] = i
        if kw.has_key('Content-Disposition'):
          content_disposition = kw['Content-Disposition']
          if content_disposition.split(';')[0] == 'attachment':
            file_name = re.findall(file_name_regexp, content_disposition, re.MULTILINE)
            if file_name:
              kw['file_name'] = file_name[0]
            else:
              kw['file_name'] = 'attachment_%s' % i
          elif content_disposition.split(';')[0] == 'inline':
            file_name = re.findall(file_name_regexp, content_disposition, re.MULTILINE)
            if file_name:
              kw['file_name'] = file_name[0]
            else:
              kw['file_name'] = 'inline_%s' % i
          else:
            kw['file_name'] = 'part_%s' % i
        if kw.has_key('Content-Type'):
          content_type = kw['Content-Type']
          file_name = re.findall(file_name_regexp, content_type, re.MULTILINE)
          if file_name: kw['file_name'] = file_name[0]
          kw['content_type'] = content_type.split(';')[0]
        result.append(kw)
      i += 1
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAttachmentData')
  def getAttachmentData(self, index, REQUEST=None):
    """
    Returns the decoded data of an attachment.
    """
    i = 0
    for part in self._getMessage().walk():
      if index == i:
        # This part should be handled in skin script
        # but it was a bit easier to access items here
        if REQUEST is not None:
          kw = dict(part.items())
          RESPONSE = REQUEST.RESPONSE
          RESPONSE.setHeader('Accept-Ranges', 'bytes')
          if kw.has_key('Content-Type'):
            RESPONSE.setHeader('Content-Type', kw['Content-Type'])
            content_type = kw['Content-Type']
          elif kw.has_key('Content-type'):
            RESPONSE.setHeader('Content-Type', kw['Content-type'])
            content_type = kw['Content-type']
          else:
            content_type = None
          if kw.has_key('Content-Disposition'):
            content_disposition = kw['Content-Disposition']
          elif kw.has_key('Content-disposition'):
            content_disposition = kw['Content-disposition']
          else:
            content_disposition = None
          file_name = None
          if content_type:
            file_name = re.findall(file_name_regexp, content_type, re.MULTILINE)
          if content_disposition:
            if not file_name:
              file_name = re.findall(file_name_regexp, content_disposition, re.MULTILINE)
          if file_name:
            file_name = file_name[0]
            RESPONSE.setHeader('Content-disposition', 'attachment; filename="%s"' % file_name)
        return part.get_payload(decode=1)
      i += 1
    return KeyError, "No attachment with index %s" % index

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
    if '\r' in subject:
      subject = ''.join(subject.split('\r'))
    if '\n' in subject:
      subject = ''.join(subject.split('\n'))
    return subject
  
  def title_or_id(self):
    """Return the title if it is not blank and the id otherwise.
    """
    return self.getTitleOrId()

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
    
    TODO: add support for legacy objects
    """
    if not self.hasFile() or self._baseGetTextContent() is not None:
      # Return the standard text content if no file was provided
      # Or standard text content is not empty.
      if default is _MARKER:
        return self._baseGetTextContent()
      else:
        return self._baseGetTextContent(default)

    # find from mail message
    text_result = None
    html_result = None
    for part in self._getMessage().walk():
      if part.get_content_type() == 'text/plain' and not text_result and not part.is_multipart():
        part_encoding = part.get_content_charset()
        if part_encoding not in (None, 'utf-8',):
          try:
            text_result = part.get_payload(decode=1).decode(part_encoding).encode('utf-8')
          except (UnicodeDecodeError, LookupError):
            text_result = part.get_payload(decode=1)
        else:
          text_result = part.get_payload(decode=1)
      elif part.get_content_type() == 'text/html' and not html_result and not part.is_multipart():
        part_encoding = part.get_content_charset()
        if part_encoding not in (None, 'utf-8',):
          try:
            text_result = part.get_payload(decode=1).\
                          decode(part_encoding).encode('utf-8')
          except (UnicodeDecodeError, LookupError):
            text_result = part.get_payload(decode=1)
        else:
          text_result = part.get_payload(decode=1)
    if default is _MARKER:
      return text_result
    return text_result or default

  security.declareProtected(Permissions.AccessContentsInformation, 'getTextFormat')
  def getTextFormat(self, default=_MARKER):
    """
    Returns the format of the email (text or html).
    
    TODO: add support for legacy objects
    """
    if not self.hasFile():
      # Return the standard text format if no file was provided
      if default is _MARKER:
        return self._baseGetTextFormat()
      else:
        return self._baseGetTextFormat(default)
    for part in self._getMessage().walk():
      if part.get_content_type() == 'text/html' and not part.is_multipart():
        return 'text/html'
    return 'text/plain'

  # Conversion API
  def _convertToBaseFormat(self):
    """
      Build a structure which can be later used
      to extract content information from this mail
      message.
    """
    pass

  security.declareProtected(Permissions.View, 'index_html')
  index_html = TextDocument.index_html

  security.declareProtected(Permissions.View, 'convert')
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
    if self.getTextFormat() == 'text/plain':
      body = self.asText()
      if body:
        return '> ' + str(body).replace('\n', '\n> ')
    elif self.getTextFormat() == 'text/html':
      return '<br/><blockquote type="cite">\n%s\n</blockquote>' %\
                                self.serializeAndCleanHtmlContentForFCKEditor()
    return ''

  security.declareProtected(Permissions.AccessContentsInformation,
                            'serializeAndCleanHtmlContentForFCKEditor')
  def serializeAndCleanHtmlContentForFCKEditor(self, html_text=None):
    """
    For FCKEditor Compatibility, we should remove DTD,
    blank lines and some tags in html document
    """
    if html_text is None:
      html_text = self.getTextContent()
    if not html_text:
      return html_text
    if not import_libxml2:
      return html_text
    #Null char. is not allowed by parser
    html_text = html_text.replace(chr(0), '')
    exclude_tag_list = ('html', 'head', 'body',)
    xsl_as_string = """<?xml version="1.0" ?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output omit-xml-declaration="yes" indent="no"/>
  <xsl:template match="/">
    <xsl:apply-templates select="*|@*|text()|comment()|processing-instruction()"/>
  </xsl:template>

  <xsl:template match="*|@*|text()|comment()|processing-instruction()">
    <xsl:copy select=".">
      <xsl:apply-templates select="*|@*|text()|comment()|processing-instruction()"/>
    </xsl:copy>
  </xsl:template>

  <xsl:template match="%s">
    <xsl:apply-templates select="*|text()|comment()|processing-instruction()"/>
  </xsl:template>

</xsl:stylesheet>
  """ % ('|'.join(exclude_tag_list))
    html_doc = libxml2.htmlParseDoc(html_text, None)
    stylesheet_doc = libxml2.parseDoc(xsl_as_string)
    stylesheet = libxslt.parseStylesheetDoc(stylesheet_doc)
    result_doc = stylesheet.applyStylesheet(html_doc, None)
    clean_text = result_doc.serialize('utf-8', 0)
    html_doc.freeDoc()
    result_doc.freeDoc()
    stylesheet.freeStylesheet()
    #Remove All xml declarations
    clean_text = re.sub('<\?xml.*\?>', '', clean_text).strip()
    #Remove blank and new Lines
    new_text_list = []
    for line in clean_text.split('\n'):
      line = line.strip()
      if line:
        new_text_list.append(line)
    clean_text = '\n'.join(new_text_list)
    return clean_text

  security.declareProtected(Permissions.AccessContentsInformation, 'getReplySubject')
  def getReplySubject(self):
    """
      This is used in order to respond to a mail,
      this put a 'Re: ' before the orignal subject
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
  def send(self, from_url=None, to_url=None, reply_url=None, subject=None,
           body=None, attachment_format=None, attachment_list=None, download=False):
    """
      Sends the current event content by email. If documents are
      attached through the aggregate category, enclose them.

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
      if sender.getTitle():
        from_url = '"%s" <%s>' % (sender.getTitle(),
                                sender.getDefaultEmailText())
      else:
        from_url = sender.getDefaultEmailText()

    # Return-Path
    if reply_url is None:
      reply_url = self.portal_preferences.getPreferredEventSenderEmail()
    additional_headers = None
    if reply_url:
      additional_headers = {'Return-Path':reply_url}

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
    elif type(to_url) in types.StringTypes:
      to_url_list.append(to_url)

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
        elif getattr(attachment, 'getTextFormat', None) is not None:
          mime_type = attachment.getTextFormat()
        else:
          raise ValueError, "Cannot find mimetype of the document."

        if mime_type is not None:
          try:
            mime_type, content = attachment.convert(mime_type)
          except ConversionError:
            mime_type = attachment.getBaseContentType()
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
                              'name':attachment.getReference()}
                             )

    for to_url in to_url_list:
      mime_message = buildEmailMessage(from_url=from_url, to_url=to_url,
                                       msg=body, subject=subject,
                                       attachment_list=attachment_list,
                                       additional_headers=additional_headers)
      mail_message = mime_message.as_string()
      self.activate(activity='SQLQueue').sendMailHostMessage(mail_message)

    # Save one of mail messages.
    self.setData(mail_message)

    # Only for debugging purpose
    if download:
      return mail_message

  security.declareProtected(Permissions.UseMailhostServices, 'sendMailHostMessage')
  def sendMailHostMessage(self, message):
    """
      Send one by one
    """
    self.MailHost.send(message)

## Compatibility layer
#from Products.ERP5Type import Document
#Document.MailMessage = EmailDocument
