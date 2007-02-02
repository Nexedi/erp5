##############################################################################
#
# Copyright (c) 2002-2006 Nexedi SARL and Contributors. All Rights Reserved.
#                         Jean-Paul Smets-Solanes <jp@nexedi.com>
#                         Kevin Deldycke          <kevin@nexedi.com>
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

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo

from Products.CMFMailIn.MailMessage import MailMessage as CMFMailInMessage
from Products.ERP5Type import Permissions, PropertySheet, Constraint, Interface
from Products.CMFCore.WorkflowCore import WorkflowMethod

from Products.ERP5.Document.Event import Event
import smtplib

from zLOG import LOG

# TODO: support "from"/"to" field header QP decoding exemple:
# =?iso-8859-15?q?K=E9vin=20De?= <kevin.de@machin.com>

# Support mail decoding in both python v2.3 and v2.4.
# See http://www.freesoft.org/CIE/RFC/1521/5.htm for 'content-transfer-encoding' explaination.
import binascii
try:
  # python v2.3 API
  from base64 import decodestring as b64decode
except AttributeError:
  # python v2.4 API
  from base64 import b64decode
global supported_decoding
supported_decoding = {
    'base64'          : b64decode
  , 'quoted-printable': binascii.a2b_qp
  # "8bit", "7bit", and "binary" values all mean that NO encoding has been performed
  , '8bit'            : None
  , '7bit'            : None
  , 'binary'          : None
  }


class MailMessage(Event, CMFMailInMessage):
  """
    MailMessage subclasses Event objects to implement Email Events.
  """

  meta_type       = 'ERP5 Mail Message'
  portal_type     = 'Mail Message'
  add_permission  = Permissions.AddPortalContent
  isPortalContent = 1
  isRADContent    = 1

  # Declarative security
  security = ClassSecurityInfo()
  security.declareObjectProtected(Permissions.AccessContentsInformation)

  # Declarative properties
  property_sheets = ( PropertySheet.Base
                    , PropertySheet.XMLObject
                    , PropertySheet.DublinCore
                    , PropertySheet.Task
                    , PropertySheet.Arrow
                    , PropertySheet.Movement
                    , PropertySheet.Event
                    , PropertySheet.MailMessage
                    )

  # default empty attributes
  header = '{}'
  body = ''

####### TODO: support attachments !!!!
#   def __init__(self, *args, **kw):
#     XMLObject.__init__(self, *args, **kw)
#     # Save attachments in a special variable
#     attachments = kw.get('attachments', {})
#     if kw.has_key('attachments'):
#       del kw['attachments']
#     self.attachments = attachments

  def _edit(self, *args, **kw):
    Event._edit(self, *args, **kw)
    self.cleanMessage()

  def cleanMessage(self):
    """
      Clean up the the message data to have UTF-8 encoded body and a clean header.
    """
    # Update the body to the clean one
    self.body = self.getBody()
    # Update the charset and the encoding since the body is known has 'cleaned'
    header = self.getHeader()
    if header != None:
      header = self.setBodyCharsetFromDict(header, charset="utf-8")
      header['content-transfer-encoding'] = "binary"
    self.header = header

  def getDecodedBody(self, raw_body, encoding):
    """
      This method return a decoded body according the given parameter.
      This method use the global "supported_decoding" dict which contain decoded
        methods supported by the current python environnment.
    """
    decoded_body = raw_body
    if encoding in supported_decoding.keys():
      method = supported_decoding[encoding]
      # Is the body encoded ?
      if method != None:
        decoded_body = method(raw_body)
    elif encoding not in (None, ''):
      raise 'MailMessage Body Decoding Error', "Body encoding '%s' is not supported" % (encoding)
    return decoded_body

  def getEncodedBody(self, body, output_charset="utf-8"):
    """
      Return the entire body message encoded in the given charset.
    """
    header       = self.getHeader()
    body_charset = self.getBodyCharsetFromDict(header)
    if body_charset != None and body_charset.lower() != output_charset.lower():
      unicode_body = unicode(body, body_charset)
      return unicode_body.encode(output_charset)
    return body

  def getBodyEncodingFromDict(self, header={}):
    """
      Extract the encoding of the body from header metadatas.
    """
    encoding = None
    if type(header) == type({}) and header.has_key('content-transfer-encoding'):
      encoding = header['content-transfer-encoding']
    return encoding

  def getBodyCharsetFromDict(self, header):
    """
      Extract the charset from the header.
    """
    charset = "utf-8"
    if header != None and header.has_key('content-type'):
      content_type = header['content-type'].replace('\n', ' ')
      content_type_info = content_type.split(';')
      for ct_info in content_type_info:
        info = ct_info.strip().lower()
        if info.startswith('charset='):
          charset = info[len('charset='):]
          # Some charset statements are quoted
          if charset.startswith('"') or charset.startswith("'"): charset = charset[1:]
          if charset.endswith(  '"') or charset.endswith(  "'"): charset = charset[:-1]
          break
    return charset

  def setBodyCharsetFromDict(self, header, charset):
    """
      This method update charset info of the body.
    """
    if header != None:
      # Update content-type where charset is stored
      content_type_info = []
      if header.has_key('content-type'):
        content_type = header['content-type'].replace('\n', ' ')
        content_type_info = content_type.split(';')
      # Force content-type charset to UTF-8
      new_content_type_metadata = []
      # Get previous info
      for ct_info in content_type_info:
        info = ct_info.strip().lower()
        # Bypass previous charset info
        if not info.startswith('charset='):
          new_content_type_metadata.append(ct_info.strip())
      # Add a new charset info consistent with the actual body charset encoding
      new_content_type_metadata.append("charset='%s'" % (charset))
      # Inject new content-type in the header
      header['content-type'] = ";\n ".join(new_content_type_metadata)
    return header

  def updateCharset(self, charset="utf-8"):
    """
      This method update charset info stored in the header.
      Usefull to manually debug bad emails.
    """
    header = self.getHeader()
    self.header = self.setBodyCharsetFromDict(header, charset)

  def getHeader(self):
    """
      Get the header dict of the message.
    """
    header = self.header
    if header == None or type(header) == type({}):
      return header
    elif type(header) == type(''):
      # Must do an 'eval' because the header is a dict stored as a text (see ERP5/PropertySheet/MailMessage.py)
      return eval(header)
    else:
      raise 'TypeError', "Type of 'header' property can't be guessed."

  def getBody(self):
    """
      Get a clean decoded body.
    """
    encoding = self.getBodyEncodingFromDict(self.getHeader())
    body_string = self.getDecodedBody(self.body, encoding)
    return self.getEncodedBody(body_string, output_charset="utf-8")

  def getReplyBody(self):
    """
      This is used in order to respond to a mail,
      this put a '> ' before each line of the body
    """
    reply_body = ''
    body = self.getBody()
    if type(body) is type('a'):
      reply_body = '> ' + body.replace('\n', '\n> ')
    return reply_body

  def getReplySubject(self):
    """
      This is used in order to respond to a mail,
      this put a 'Re: ' before the orignal subject
    """
    reply_subject = self.getTitle()
    if reply_subject.find('Re: ') != 0:
      reply_subject = 'Re: ' + reply_subject
    return reply_subject

  def send(self, from_url=None, to_url=None, msg=None, subject=None):
    """
      Sends a reply to this mail message.
    """
    # We assume by default that we are replying to the sender
    if from_url == None:
      from_url = self.getUrlString()
    if to_url == None:
      to_url = self.getSender()
    if msg is not None and subject is not None:
      header  = "From: %s\n"    % from_url
      header += "To: %s\n\n"    % to_url
      header += "Subject: %s\n" % subject
      header += "\n"
      msg = header + msg
      self.MailHost.send( msg )
