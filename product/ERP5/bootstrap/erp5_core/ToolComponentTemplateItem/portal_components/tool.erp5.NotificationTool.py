# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2009 Nexedi SA and Contributors. All Rights Reserved.
#                    Sebastien Robin <seb@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
from six import string_types as basestring
from AccessControl import ClassSecurityInfo
from Products.ERP5Type.Tool.BaseTool import BaseTool
from Products.ERP5Type import Permissions
from AccessControl import ModuleSecurityInfo
from zExceptions import Unauthorized

from mimetypes import guess_type
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.utils import formataddr
from email.header import make_header
from email import encoders

class ConversionError(Exception): pass
class MimeTypeException(Exception): pass

from AccessControl.SecurityInfo import allow_module
allow_module(__name__)

security = ModuleSecurityInfo(__name__)
security.declarePublic('buildEmailMessage',)

def buildAttachmentDictList(document_list, document_type_list=()):
  """return a list of dictionary which will be used by buildEmailMessage"""
  attachment_list = []
  for attachment in document_list:
    mime_type = None
    content = None
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
        raise ValueError("Cannot find mimetype of the document.")

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
                            'name':attachment.getStandardFilename()}
                           )
  return attachment_list


def buildEmailMessage(from_url, to_url, msg=None,
                      subject=None, attachment_list=None,
                      extra_headers=None,
                      additional_headers=None):
  """
    Builds a mail message which is ready to be
    sent by Zope MailHost.

    * attachment_list is a list of dictionaries with those keys:
     - name (str): name of the attachment
     - content (bytes): data of the attachment
     - mime_type (str): mime-type corresponding to the attachment
    * extra_headers is a dictionary of custom headers to add to the email.
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

  if subject:
    message.add_header('Subject',
                        make_header([(subject, 'utf-8')]).encode())
  if from_url:
    message.add_header('From', from_url)
  if to_url:
    message.add_header('To', to_url)

  for attachment in attachment_list:
    attachment_name = attachment.get('name', '')

    # try to guess the mime type
    if 'mime_type' not in attachment:
      mime_type, _ = guess_type( attachment_name )
      if mime_type is not None:
        attachment['mime_type'] = mime_type
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
        encoders.encode_base64(part)

    part.add_header('Content-Disposition', 'attachment',
                    filename=attachment_name)
    part.add_header('Content-ID', '<%s>' % \
                    ''.join(['%s' % ord(i) for i in attachment_name]))
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
  title = 'Notifications'

  # Declarative Security
  security = ClassSecurityInfo()

  # low-level interface
  def _sendEmailMessage(self, from_url, to_url, body=None, subject=None,
                        attachment_list=None, extra_headers=None,
                        additional_headers=None, debug=False):
    portal = self.getPortalObject()
    mailhost = getattr(portal, 'MailHost', None)
    if mailhost is None:
      raise ValueError("Can't find MailHost.")
    message = buildEmailMessage(from_url, to_url, msg=body, subject=subject,
                                attachment_list=attachment_list, extra_headers=extra_headers,
                                additional_headers=additional_headers)

    if debug:
      return message.as_string()

    mailhost.send(messageText=message.as_string(), mto=to_url, mfrom=from_url)

  # high-level interface
  security.declareProtected(Permissions.UseMailhostServices, 'sendMessage')
  def sendMessage(self, sender=None, recipient=None, subject=None,
                  message=None,
                  attachment_list=None, attachment_document_list=None,
                  notifier_list=None, priority_level=None,
                  store_as_event=False,
                  check_consistency=False,
                  message_text_format='text/plain',
                  event_keyword_argument_dict=None,
                  portal_type_list=None,
                  REQUEST=None):
    """
      This method provides a common API to send messages to erp5 users
      from object actions of workflow scripts.

      Note that you can't send message to person who don't have his own Person document.
      This method provides only high-level functionality so that you can't use email address
      for sender and recipient, or raw data for attachments.

      sender -- a user id or a user document

      recipient -- a user id or a user document, or a list thereof

      subject -- the subject of the message

      message -- the text of the message (already translated)

      attachment_list -- list of dictionary which contains raw data and
                         name and mimetype for attachment.
                         See buildEmailMessage.

      attachment_document_list -- list of document (optional)
                                  which will be attachment.

      priority_level -- a priority level which is used to
                        lookup user preferences and decide
                        which notifier to use
                        XXX Not implemented yet!!

      notifier_list -- a list of portal type names to use
                       to send the event

      store_as_event -- whenever CRM is available, store
                        notifications as events

      check_consistency -- Check that the created events match their constraints.
                           If any of the event have an unsatisified constraint, a
                           ValueError is raised.
                           Note that if `store_as_event` is true, some draft
                           events are created anyway, so caller may want to
                           abort transaction.

      event_keyword_argument_dict -- additional keyword arguments which is used for
                                     constructor of event document.

    TODO: support default notification email
    """
    if REQUEST is not None:
      raise Unauthorized()
    portal = self.getPortalObject()
    searchUsers = self.acl_users.searchUsers
    def getUserValueByUserId(user_id):
      user, = [x for x in searchUsers(id=user_id, exact_match=True,
               login_portal_type=portal.getPortalLoginTypeList()) if 'path' in x]
      return portal.unrestrictedTraverse(user['path'])

    if notifier_list is None:
      # XXX TODO: Use priority_level. Need to implement default notifier query system.
      # XXX       For now, we use 'Mail Message'.
      notifier_list = ['Mail Message']
    if not isinstance(notifier_list, (tuple, list)):
      raise TypeError("Notifier list must be a list of portal types")

    if not subject:
      raise TypeError("subject is required")

    # Find "From" Person
    from_person = None
    if isinstance(sender, basestring):
      sender = getUserValueByUserId(sender)
    if sender is not None:
      email_value = sender.getDefaultEmailValue()
      if email_value is not None and email_value.asText():
        from_person = sender

    # Find "To" Person list
    to_person_list = []
    # XXX: evaluating a document as boolean is bad, as __bool__ may be
    # overloaded to (for example) return False if there are no children (which
    # would have unintended effects here).
    if recipient:
      if not isinstance(recipient, (list, tuple)):
        recipient = (recipient, )
      for person in recipient:
        if isinstance(person, basestring):
          person_value = getUserValueByUserId(person)
          if person_value is None:
            raise ValueError("Can't find user with id %r" % (person, ))
          person = person_value
        to_person_list.append(person)

    # prepare low-level arguments if needed.
    low_level_kw = {}
    default_from_email = portal.email_from_address
    default_to_email = getattr(portal, 'email_to_address',
                               default_from_email)
    default_from_name = portal.title
    default_from_name = getattr(portal, 'email_from_name', default_from_name)
    if from_person is None:
      # when sending without sender defined compose identifiable From header
      low_level_kw['from_url'] = formataddr((default_from_name, default_from_email))
    if not to_person_list:
      low_level_kw['to_url'] = default_to_email
    if attachment_list is not None:
      low_level_kw['attachment_list'] = attachment_list

    # Make event
    available_notifier_list = self.getNotifierList()
    event_list = []
    if event_keyword_argument_dict is None:
      event_keyword_argument_dict = {}
    for notifier in notifier_list:
      if notifier not in available_notifier_list:
        raise TypeError("%r not in available Notifiers %r" %
                        (notifier, available_notifier_list))
      # If it is not going to be stored, no need to create it in a specific
      # Module, especially considering that it may not be available such as
      # `Event Module` (erp5_crm) for `Mail Message` (erp5_base) notifier
      if not store_as_event:
        event = portal.newContent(portal_type=notifier, temp_object=True,
                                  **event_keyword_argument_dict)
      else:
        event = portal.getDefaultModule(notifier).newContent(portal_type=notifier,
                                                             **event_keyword_argument_dict)

      event.setSourceValue(from_person)
      event.setDestinationValueList(to_person_list)
      event.setTitle(subject)
      event.setContentType(message_text_format)
      event.setTextContent(message)
      event.setAggregateValueList(attachment_document_list)
      event_list.append(event)

    if check_consistency:
      for event in event_list:
        constraint_message_list = event.checkConsistency()
        if constraint_message_list:
          raise ValueError(constraint_message_list)

    for event in event_list:
      if event.isTempObject() or (not portal.portal_workflow.isTransitionPossible(event, 'start')):
        event.send(**low_level_kw)
      else:
        event.start(**low_level_kw)

    return
    # Future implementation could consist in implementing
    # policies such as grouped notification (per hour, per day,
    # per week, etc.) depending on user preferences. It
    # also add some priority and selection of notification
    # tool (ex SMS vs. email)

    # Here is a sample code of how this implementation could look like
    # (pseudo code)
    # NOTE: this implementation should also make sure that the current
    # buildEmailMessage method defined here and the Event.send method
    # are merged once for all
    #
    #if self.getNotifierList():
    #  # CRM is installed - so we can lookup notification preferences
    #  if notifier_list is None:
    #    # Find which notifier to use on preferences
    #    if priority_level not in ('low', 'medium', 'high'): # XXX Better naming required here
    #      priority_level = 'high'
    #    notifier_list = self.preferences.getPreference(
    #          'preferred_%s_priority_nofitier_list' % priority_level)
    #  event_list = []
    #  for notifier in notifier_list:
    #    event_module = self.getDefaultModule(notifier)
    #    new_event = event_module.newContent(portal_type=notifier, temp_object=store_as_event)
    #    event_list.append(new_event)
    #else:
    #  # CRM is not installed - only notification by email is possible
    #  # So create a temp object directly
    #  new_event = self.newContent(temp_object=True, portal_type='Event', id='_')
    #  event_list = [new_event]
    #
    #if event in event_list:
    #  # We try to build events using the same parameters as the one
    #  # we were provided for notification.
    #  # The handling of attachment is still an open question:
    #  # either use relation (to prevent duplication) or keep
    #  # a copy inside. It is probably a good idea to
    #  # make attachment_list polymorphic in order to be able
    #  # to provide different kinds of attachments can be provided
    #  # Either document references or binary data.
    #  event.build(sender=sender, recipient=recipient, subject=subject,
    #              message=message, attachment_list=attachment_list,) # Rename here and add whatever
    #                                                                 # parameter makes sense such
    #                                                                 # as text format
    #  event.send() # Make sure workflow transition is invoked if this is
    #               # a persistent notification
    #
    #  # Aggregation could be handled by appending the notification
    #  # to an existing message rather than creating a new one.
    #  # Sending the message should be handled by the alarm based
    #  # on a date value stored on the event. This probably required
    #  # a new workflow state to represent events which are waiting
    #  # for being sent automatically. (ie. scheduled sending)

  security.declareProtected(Permissions.AccessContentsInformation, 'getNotifierList')
  def getNotifierList(self):
    """
      Returns the list of available notifiers. For now
      we consider that any event is a potential notifier.
      This could change though.
    """
    return self.getPortalEventTypeList()

  security.declareProtected(Permissions.AccessContentsInformation, 'getDocumentValue')
  def getDocumentValue(self, **kw):
    """
      Returns the last version of a Notification Document in selected Language.
    """
    method = self._getTypeBasedMethod('getDocumentValue')
    return method(**kw)

  def __call__(self, *args, **kw):
    return self.sendMessage(*args, **kw)
