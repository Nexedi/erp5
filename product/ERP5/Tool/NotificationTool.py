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
from AccessControl import ClassSecurityInfo
from Globals import DTMLFile
from Products.CMFCore.utils import getToolByName
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from Products.ERP5 import _dtmldir

from mimetypes import guess_type
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email.MIMEAudio import MIMEAudio
from email.MIMEImage import MIMEImage
from email.Header import make_header
from email import Encoders


def buildEmailMessage(from_url, to_url, msg=None,
                      subject=None, attachment_list=None,
                      extra_headers=None,
                      additional_headers=None):
  """
    Builds a mail message which is ready to be
    sent by Zope MailHost.

    * attachment_list is a list of dictionnaries with those keys:
     - name : name of the attachment,
     - content: data of the attachment
     - mime_type: mime-type corresponding to the attachment
    * extra_headers is a dictionnary of custom headers to add to the email.
      "X-" prefix is automatically added to those headers.
    * additional_headers is similar to extra_headers, but no prefix is added.
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
    for key, value in extra_headers.items():
      message.add_header('X-%s' % key, value)

  if additional_headers:
    for key, value in additional_headers.items():
      message.add_header(key, value)

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
      major, minor = attachment['mime_type'].split('/', 1)
      if major == 'text':
        part = MIMEText(attachment['content'], _subtype=minor)
      elif major == 'image':
        part = MIMEImage(attachment['content'], _subtype=minor)
      elif major == 'audio':
        part = MIMEAudio(attachment['content'], _subtype=minor)
      else:
        #  encode non-plaintext attachment in base64      
        part = MIMEBase(major, minor)
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

  # XXX Bad Name...Any Idea?
  security.declareProtected(Permissions.UseMailhostServices, 'sendMessageLowLevel')
  def sendMessageLowLevel(self, from_url, to_url, body=None, subject=None,
                          attachment_list=None, extra_headers=None, additional_headers=None,
                          debug=False):
    portal = self.getPortalObject()
    mailhost = getattr(portal, 'MailHost', None)
    if mailhost is None:
      raise ValueError, "Can't find MailHost."
    message = buildEmailMessage(from_url, to_url, msg=body, subject=subject,
                                attachment_list=attachment_list, extra_headers=extra_headers,
                                additional_headers=additional_headers)

    if debug:
      return message.as_string()

    mailhost.send(messageText=message.as_string(), mto=to_url, mfrom=from_url)

  security.declareProtected(Permissions.UseMailhostServices, 'sendMessage')
  def sendMessage(self, sender=None, recipient=None, subject=None, 
                        message=None, attachment_list=None,
                        notifier_list=None, priority_level=None,
                        is_persistent=False):
    """
      This method provides a common API to send messages to erp5 users
      from object actions of worflow scripts.

      Note that you can't send message to person who don't have his own Person document.

      sender -- a login name(reference of Person document) or a Person document

      recipient -- a login name(reference of Person document) or a Person document,
                   a list of thereof

      subject -- the subject of the message

      message -- the text of the message (already translated)

      attachment_list -- list of dictionary (optional)
                         keys are: name, content, mime_type
                         See buildEmailMessage function above.

      priority_level -- a priority level which is used to
                        lookup user preferences and decide
                        which notifier to use

      notifier_list -- a list of portal type names to use
                       to send the event

      is_persistent -- whenever CRM is available, store
                       notifications as events

    TODO: support default notification email
    """
    portal = self.getPortalObject()
    catalog_tool = getToolByName(self, 'portal_catalog')

    # Find Default Values
    default_from_email = portal.email_from_address
    default_to_email = getattr(portal, 'email_to_address',
                               default_from_email)

    # Find "From" address
    from_address = None
    if isinstance(sender, basestring):
      sender = catalog_tool.getResultValue(portal_type='Person', reference=sender)
    if sender is not None:
      email_value = sender.getDefaultEmailValue()
      if email_value is not None:
        from_address = email_value.asText()
    if not from_address:
      # If we can not find a from address then
      # we fallback to default values
      from_address = default_from_email

    # Find "To" addresses
    to_address_list = []
    if not recipient:
      to_address_list.append(default_to_email)
    else:
      if not isinstance(recipient, (list, tuple)):
        recipient = (recipient,)
      for person in recipient:
        if isinstance(person, basestring):
          person = catalog_tool.getResultValue(portal_type='Person', reference=person)
          if person is None:
            # For backward compatibility. I recommend to use ValueError.(yusei)
            raise IndexError, "Can't find person document which reference is '%s'" % person
        email_value = person.getDefaultEmailValue()
        if email_value is None:
          # For backward compatibility. I recommend to use ValueError.(yusei)
          raise AttributeError, "Can't find default email address of %s" % person.getRelativeUrl()
        to_address_list.append(email_value.asText())

    # Build and Send Messages
    for to_address in to_address_list:
      self.sendMessageLowLevel(from_url=from_address,
                               to_url=to_address,
                               body=message,
                               subject=subject,
                               attachment_list=attachment_list
                               )

    return
    # Future implemetation could consist in implementing
    # policies such as grouped notification (per hour, per day,
    # per week, etc.) depending on user preferences. It
    # also add some priority and selection of notification
    # tool (ex SMS vs. email)

    # Here is a sample code of how this implementation could look like
    # (pseudo code)
    # NOTE: this implementation should also make sure that the current
    # buildEmailMessage method defined here and the Event.send method
    # are merged once for all

    if self.getNotifierList():
      # CRM is installed - so we can lookup notification preferences
      if notifier_list is None:
        # Find which notifier to use on preferences
        if priority_level not in ('low', 'medium', 'high'): # XXX Better naming required here
          priority_level = 'high'
        notifier_list = self.preferences.getPreference(
              'preferred_%s_priority_nofitier_list' % priority_level)
      event_list = []
      for notifier in notifier_list:
        event_module = self.getDefaultModule(notifier)
        new_event = event_module.newContent(portal_type=notifier, temp_object=is_persistent)
        event_list.append(new_event)
    else:
      # CRM is not installed - only notification by email is possible
      # So create a temp object directly
      from Products.ERP5Type.Document import newTempEvent
      new_event = newTempEvent(context, '_')
      event_list = [new_event]

    if event in event_list:
      # We try to build events using the same parameters as the one
      # we were provided for notification.
      # The handling of attachment is still an open question:
      # either use relation (to prevent duplication) or keep
      # a copy inside. It is probably a good idea to
      # make attachment_list polymorphic in order to be able
      # to provide different kinds of attachments can be provided
      # Either document references or binary data.
      event.build(sender=sender, recipient=recipient, subject=subject, 
                  message=message, attachment_list=attachment_list,) # Rename here and add whatever
                                                                     # parameter makes sense such
                                                                     # as text format
      event.send() # Make sure workflow transition is invoked if this is
                   # a persistent notification

      # Aggregation could be handled by appending the notification
      # to an existing message rather than creating a new one.
      # Sending the message should be handled by the alarm based
      # on a date value stored on the event. This probably required
      # a new workflow state to represent events which are waiting
      # for being sent automatically. (ie. scheduled sending)

  security.declareProtected(Permissions.AccessContentsInformation, 'getNotifierList')
  def getNotifierList(self):
    """
      Returns the list of available notifiers. For now
      we consider that any event is a potential notifier.
      This could change though.
    """
    return self.getPortalEventTypeList()
