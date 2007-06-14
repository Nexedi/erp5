##############################################################################
#
# Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
# Copyright (c) 2006 Nexedi SARL and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################

import mimetypes
import email
from email.Header import decode_header, make_header
from email.Utils import parseaddr
from ZODB.POSException import ConflictError
from zLOG import LOG

import traceback
import StringIO

from Products.CMFMailIn.MailIn_Tool import MailInTool

# Add new method on MailInTool
def MailInTool_postUTF8MailMessage(self, file=None):
  """
  Recode the email in UTF-8 in order to import it 
  in ERP5.
  """
  if not file:
      raise IOError, 'No Mail Message Supplied'
  # Prepare result
  theMail = {
    'attachment_list': [],
    'body': '',
    # Place all the email header in the headers dictionary in theMail
    'headers': {}
  }
  # Get Message
  msg = email.message_from_string(file)
  # Back up original file
  theMail['__original__'] = file
  # Recode headers to UTF-8 if needed
  for key, value in msg.items():
    decoded_value_list = decode_header(value)
    unicode_value = make_header(decoded_value_list)
    new_value = unicode_value.__unicode__().encode('utf-8')
    theMail['headers'][key.lower()] = new_value
  # Filter mail addresses
  for header in ('resent-to', 'resent-from', 'resent-cc', 'resent-sender', 'to', 'from', 'cc', 'sender', 'reply-to'):
    header_field = theMail['headers'].get(header)
    if header_field:
        theMail['headers'][header] = parseaddr(header_field)[1]
  # Get attachments
  body_found = 0
  for part in msg.walk():
    content_type = part.get_content_type()
    file_name = part.get_filename()
    # multipart/* are just containers
    # XXX Check if data is None ?
    if content_type.startswith('multipart'):
      continue
    # message/rfc822 contains attached email message
    # next 'part' will be the message itself
    # so we ignore this one to avoid doubling
    elif content_type == 'message/rfc822':
      continue
    elif content_type == "text/plain":
      charset = part.get_content_charset()
      payload = part.get_payload(decode=True)
      #LOG('CMFMailIn -> ',0,'charset: %s, payload: %s' % (charset,payload))
      if charset:
        payload = unicode(payload, charset).encode('utf-8')
      if body_found:
        # Keep the content type
        theMail['attachment_list'].append((file_name, 
                                           content_type, payload))
      else:
        theMail['body'] = payload
        body_found = 1
    else:
      payload = part.get_payload(decode=True)
      # Keep the content type
      theMail['attachment_list'].append((file_name, content_type, 
                                         payload))
  portal_url = self.portal_url.getPortalPath()
  if (portal_url != '') and (portal_url[-1] != '/'): 
    portal_url = portal_url+'/'
      
  if self.method:
    try:
      return self.restrictedTraverse(portal_url+self.method)\
                                                    (theMail=theMail)
    except ConflictError:
      # XXX Warning: if exception is raised, the MTA will
      # not return the mail to the sender
      raise
    except:
      # It's needed to catch all exceptions, as we need to return
      # a value to the MTA in this case.

      # Generate log message
      fp = StringIO.StringIO()
      traceback.print_exc(file=fp)
      log_message = fp.getvalue()
      LOG("GeneratorTool, next", 1000, 
          log_message)
      return "Message rejected. \n %s" % log_message
  
  self.REQUEST.RESPONSE.notFoundError('MailIn method not specified')

MailInTool.postUTF8MailMessage = MailInTool_postUTF8MailMessage
