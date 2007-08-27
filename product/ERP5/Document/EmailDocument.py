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
from time import mktime
from Globals import get_request

from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Base import WorkflowMethod
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import _setCacheHeaders
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.ERP5.Document.TextDocument import TextDocument
from Products.ERP5.Document.File import File
from Products.CMFDefault.utils import isHTMLSafe

from email import message_from_string
from email.Utils import parsedate
from email import Encoders
from email.Message import Message
from email.MIMEAudio import MIMEAudio
from email.MIMEBase import MIMEBase
from email.MIMEImage import MIMEImage
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

DEFAULT_TEXT_FORMAT = 'text/html'
COMMASPACE = ', '
_MARKER = []

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
    """
    result = {}
    for (name, value) in self._getMessage().items():
      result[name] = value
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
            kw['file_name'] = content_disposition.split(';')[1].split('=')[1] # Quick hack - make this better with re
          elif content_disposition.split(';')[0] == 'inline':
            kw['file_name'] = 'inline_%s' % i
          else:
            kw['file_name'] = 'part_%s' % i
        result.append(kw)
      i += 1
    return result

  security.declareProtected(Permissions.AccessContentsInformation, 'getAttachmentData')
  def getAttachmentData(self, index):
    """
    Returns the decoded data of an attachment.
    
    TODO: add support for format in RESPONSE if defined
    """
    i = 0
    for part in self._getMessage().walk():
      if index == i:
        return part.get_payload(decode=1)
      i += 1
    return KeyError, "No attachment with index %s" % index

  # Overriden methods
  security.declareProtected(Permissions.AccessContentsInformation, 'getTitle')
  def getTitle(self, default=_MARKER):
    """
    Returns the title
    """
    if not self.hasFile():
      # Return the standard text content if no file was provided
      if default is _MARKER:
        return self._baseGetTitle()
      else:
        return self._baseGetTitle(default)
    return self.getContentInformation().get('Subject', '')

  security.declareProtected(Permissions.AccessContentsInformation, 'getStartDate')
  def getStartDate(self, default=_MARKER):
    """
    Returns the title
    """
    if not self.hasFile():
      # Return the standard start date if no file was provided
      if default is _MARKER:
        return self._baseGetStartDate()
      else:
        return self._baseGetStartDate(default)
    date_string = self.getContentInformation().get('Date', None)
    if date_string:
      time = mktime(parsedate(date_string))
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
    if not self.hasFile():
      # Return the standard text content if no file was provided
      if default is _MARKER:
        return self._baseGetTextContent()
      else:
        return self._baseGetTextContent(default)
    text_result = None
    html_result = None
    for part in self._getMessage().walk():
      if part.get_content_type() == 'text/plain' and not text_result and not part.is_multipart():
        text_result = part.get_payload(decode=1)
      elif part.get_content_type() == 'text/html' and not html_result and not part.is_multipart():
        return part.get_payload(decode=1)
    return text_result

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

  index_html = TextDocument.index_html

  security.declareProtected(Permissions.View, 'convert')
  def convert(self, format, **kw):
    """
      Convert text using portal_transforms
    """
    # Accelerate rendering in Web mode
    _setCacheHeaders(self, {'format' : format})
    # Return the raw content
    if format == 'raw':
      return 'text/plain', self.getTextContent()
    mime_type = getToolByName(self, 'mimetypes_registry').lookupExtension('name.%s' % format)
    src_mimetype = self.getTextFormat(DEFAULT_TEXT_FORMAT)
    if not src_mimetype.startswith('text/'):
      src_mimetype = 'text/%s' % src_mimetype
    # check if document has set text_content and convert if necessary
    text_content = self.getTextContent()
    if text_content is not None:
      portal_transforms = getToolByName(self, 'portal_transforms')
      return mime_type, portal_transforms.convertTo(mime_type,
                                                    text_content, 
                                                    object = self, 
                                                    mimetype = src_mimetype)
    else:
      # text_content is not set, return empty string instead of None
      return mime_type, ''

  security.declareProtected(Permissions.AccessContentsInformation, 'hasBaseData')
  def hasBaseData(self):
    """ 
      Since there is no need to convert to a base format, we consider that 
      we always have the base format if we have text of file.
    """
    return self.hasFile() or self.hasTextContent()

  # Methods which can be useful to prepare a reply by email to an event
  security.declareProtected(Permissions.AccessContentsInformation, 'getReplyBody')
  def getReplyBody(self):
    """
      This is used in order to respond to a mail,
      this put a '> ' before each line of the body
    """
    body = self.asText()
    if body:
      return '> ' + str(body).replace('\n', '\n> ')
    return ''

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
                 body=None,
                 attachment_format=None, download=False):
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
                 as body

      attachment_format - defines an option format
                 to convet attachments to (ex. application/pdf)

      download - if set to True returns, the message online
                rather than sending it.

      This method is based on the examples provided by
      http://docs.python.org/lib/node162.html

      TODO: support conversion to base format and use
      base format rather than original format

      TODO2: consider turning this method into a general method for
      any ERP5 document.
    """
    # Prepare header data
    if body is None:
      body = self.asText()
    if subject is None:
      subject = self.getTitle()
    if from_url is None:
      from_url = self.getSourceValue().getDefaultEmailText()
    if reply_url is None:
      reply_url = self.portal_preferences.getPreferredEventSenderEmail()
    if to_url is None:
      for recipient in self.getDestinationValueList():
        to_url = []
        email = recipient.getDefaultEmailText()
        if email:
          to_url.append(email)
        else:
          raise ValueError, 'Recipient %s has no defined email' % recipient
    elif type(to_url) in types.StringTypes:
      to_url = [to_url]

    # Create the container (outer) email message.
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = from_url
    message['To'] = COMMASPACE.join(to_url)
    message['Return-Path'] = reply_url
    message.preamble = 'You will not see this in a MIME-aware mail reader.\n'

    # Add the body of the message
    attached_message = MIMEText(str(body))
    message.attach(attached_message)

    # Attach files
    document_type_list = self.getPortalDocumentTypeList()
    for attachment in self.getAggregateValueList():
      if attachment.getPortalType() in document_type_list:
        # If this is a document, use 
        mime_type = attachment.getContentType() # WARNING - this could fail since getContentType
                                                # is not (yet) part of Document API
        mime_type, attached_data = attachment.convert(mime_type)
      else:
        mime_type = 'application/pdf'
        attached_data = attachment.asPDF() # XXX - Not implemented yet
                                               # should provide a default printout
      if not mime_type:
        mime_type = 'application/octet-stream'
      # Use appropriate class based on mime_type
      maintype, subtype = mime_type.split('/', 1)
      if maintype == 'text':
        attached_message = MIMEText(attached_data, _subtype=subtype)
      elif maintype == 'image':
        attached_message = MIMEImage(attached_data, _subtype=subtype)
      elif maintype == 'audio':
        attached_message = MIMEAudio(attached_data, _subtype=subtype)
      else:
        attached_message = MIMEBase(maintype, subtype)
        attached_message.set_payload(attached_data)
        Encoders.encode_base64(attached_message)
      attached_message.add_header('Content-Disposition', 'attachment', filename=attachment.getReference())
      message.attach(attached_message)

    # Send the message
    if download:
      return message.as_string()

    self.MailHost.send(message.as_string())

## Compatibility layer
#from Products.ERP5Type import Document
#Document.MailMessage = EmailDocument