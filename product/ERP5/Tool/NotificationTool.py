##############################################################################
#
# Copyright (c) 2004 Nexedi SARL and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
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

import time
import threading

from AccessControl import ClassSecurityInfo
from AccessControl.SecurityManagement import newSecurityManager
from Globals import InitializeClass, DTMLFile, PersistentMapping
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Core.Folder import Folder
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir

from cStringIO import StringIO
from mimetypes import guess_type
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.Header import make_header
from email import Encoders

from zLOG import LOG, INFO

def buildEmailMessage(from_url, to_url, msg=None,
                      subject=None, attachment_list=None,
                      extra_headers=None):
  """
    Builds a mail message which is ready to be
    sent by Zope MailHost.

    * attachment_list is a list of dictionnaries with those keys:
     - name : name of the attachment,
     - content: data of the attachment
     - mime_type: mime-type corresponding to the attachment
    * extra_headers is a dictionnary of custom headers to add to the email.
      "X-" prefix is automatically added to those headers.
  """

  if attachment_list == None:
    # Create non multi-part MIME message.
    message = MIMEText(msg, _charset='utf-8')
    attachment_list = []
  else:
    # Create multi-part MIME message.
    message = MIMEMultipart()
    message.preamble = "If you can read this, your mailreader\n" \
                        "can not handle multi-part messages!\n"
    message.attach(MIMEText(msg, _charset='utf-8'))

  if extra_headers:
    for k, v in extra_headers.items():
      message.add_header('X-%s' % k, v)

  message.add_header('Subject',
                      make_header([(subject, 'utf-8')]).encode())
  message.add_header('From', from_url)
  message.add_header('To', to_url)

  for attachment in attachment_list:
    if attachment.has_key('name'):
      attachment_name = attachment['name']
    else:
      attachment_name = ''
    # try to guess the mime type
    if not attachment.has_key('mime_type'):
      type, encoding = guess_type( attachment_name )
      if type != None:
        attachment['mime_type'] = type
      else:
        attachment['mime_type'] = 'application/octet-stream'

    # attach it
    if attachment['mime_type'] == 'text/plain':
      part = MIMEText(attachment['content'], _charset='utf-8')
    else:
      #  encode non-plaintext attachment in base64
      part = MIMEBase(*attachment['mime_type'].split('/', 1))
      part.set_payload(attachment['content'])
      Encoders.encode_base64(part)

    part.add_header('Content-Disposition',
                    'attachment; filename=%s' % attachment_name)
    message.attach(part)

  return message

class NotificationTool(BaseTool):
  """
    This tool manages notifications.

    It is used as a central point to send messages from one
    user to one or many users. The purpose of the tool
    is to provide an API for sending messages which is
    independent on how messages are actually going to be
    sent and when.

    It is also useful to send messages without having to
    write always the same piece of code (eg. lookup the user,
    lookup its mail, etc.).

    This early implementation only provides asynchronous
    email sending.

    Future implementations may be able to lookup user preferences
    to decide how and when to send a message to each user.
  """
  id = 'portal_notifications'
  meta_type = 'ERP5 Notification Tool'
  portal_type = 'Notification Tool'

  # Declarative Security
  security = ClassSecurityInfo()

  security.declareProtected( Permissions.ManagePortal, 'manage_overview' )
  manage_overview = DTMLFile( 'explainNotificationTool', _dtmldir )

  security.declareProtected(Permissions.UseMailhostServices, 'sendMessage')
  def sendMessage(self, sender=None, recipient=None, subject=None, 
                  message=None, attachment_list=None):
    """
      This method provides a common API to send messages to users
      from object actions of worflow scripts.

      sender -- a string or a Person object

      recipient -- a string or a Person object
                   a list of thereof

      subject -- the subject of the message

      message -- the text of the message (already translated)

      attachment_list -- attached documents (optional)

    TODO: support default notification email
    """
    catalog_tool = getToolByName(self, 'portal_catalog')

    # Default Values
    portal = self.getPortalObject()
    default_from_email = portal.email_from_address
    default_to_email = portal.email_to_address

    # Change all strings to object values
    if isinstance(sender, basestring):
      sender = catalog_tool(portal_type='Person', reference=sender)[0]

    email_from_address = None
    if sender is not None:
      email_value = sender.getDefaultEmailValue()
      if email_value is not None:
        email_from_address = email_value.asText()
    if not email_from_address:
      # If we can not find a from address then
      # we fallback to default values
      email_from_address = default_from_email

    # To is a list - let us find all members
    if not isinstance(recipient, (list, tuple)):
      recipient = (recipient, )

    # If no recipient is defined, just send an email to the
    # default mail address defined at the CMF site root.
    if recipient is None:
      mailhost = getattr(self.getPortalObject(), 'MailHost', None)
      if mailhost is None:
        raise AttributeError, "Cannot find a MailHost object"
      mail_message = buildEmailMessage(email_from_address, default_to_email, 
                                       msg=message, subject=subject,
                                       attachment_list=attachment_list)
      return mailhost.send(mail_message.as_string(), default_to_email, email_from_address)

    # Default implementation is to send an active message to everyone
    for person in recipient:
      if isinstance(person, basestring):
        person = catalog_tool(portal_type='Person', reference=person)[0]
      email_value = person.getDefaultEmailValue()
      if email_value is not None:
        # Activity can not handle attachment
        # Queuing messages has to be managed by the MTA
        email_value.send(
                          from_url=email_from_address,
                          to_url=email_value.asText(),
                          subject=subject,
                          msg=message,
                          attachment_list=attachment_list)
      else:
        raise AttributeError, \
            "Can not contact the person %s" % person.getReference()

    # Future implemetation could consist in implementing
    # policies such as grouped notification (per hour, per day,
    # per week, etc.) depending on user preferences. It
    # also add some urgency and selection of notification
    # tool (ex SMS vs. email)
