"""Send a mail message.

This script is also used by notification tool, that's why it is in erp5_base.
"""

from email.utils import formataddr
portal = context.getPortalObject()

use_activity = False
mail_message = None
to_url_list = []

# Attachments
document_type_list = list(context.getPortalEmbeddedDocumentTypeList()) + list(context.getPortalDocumentTypeList())
embedded_file_list = context.getAggregateValueList(portal_type=document_type_list)
for attachment in attachment_list or []:
  embedded_file = context.newContent(
    portal_type='Embedded File',
    title=attachment['name'],
    filename=attachment['name'],
    content_type=attachment['mime_type'],
    data=attachment['content'],
  )
  if embedded_file not in embedded_file_list:
    embedded_file_list.append(embedded_file)
aggregate_list = context.getAggregateValueList()
context.setAggregateValueList(
  aggregate_list + [x for x in embedded_file_list if x not in aggregate_list]
)

if not context.isTempDocument() and to_url is None:
  use_activity = True

if to_url is None:
  for recipient in context.getDestinationValueList():
    email = recipient.getDefaultEmailText()
    if email:
      to_url_list.append(formataddr((recipient.hasTitle() and recipient.getTitle(), recipient.getDefaultEmailText())))
    else:
      # MailMessage portal type is supposed to have a constraint to report this
      # to the user earlier
      raise ValueError("One email must be set to %s" % recipient.getRelativeUrl())
else:
  to_url_list.append(to_url)

if not context.hasStartDate():
  context.setStartDate(DateTime())

if download or not use_activity:

  create_post_message_method = context.getTypeBasedMethod('createPostMessage')

  for to_url in to_url_list:
    body = body or context.getTextContent() or ''
    subject = subject or context.getTitle() or ''

    # From
    if from_url is None:
      sender = context.getSourceValue()
      if sender is not None:
        from_url = formataddr((sender.hasTitle() and sender.getTitle(), sender.getDefaultEmailText()))
      else:
        from_url = portal.portal_preferences.getPreferredEventSenderEmail()
        if not from_url:
          raise ValueError('Preferred Event Sender Email not configured')

    # Return-Path (TODO)
    if reply_url is None:
      reply_url = portal.portal_preferences.getPreferredEventSenderEmail()
    additional_headers = None # pylint: disable=unused-variable
    if reply_url:
      additional_headers = {'Return-Path':reply_url}
    content_type = context.getContentType()

    mail_message = context.Base_createMailMessageAsString(
      from_url,
      to_url,
      subject,
      body,
      content_type,
      embedded_file_list=embedded_file_list,
      extra_header_dict=extra_header_dict)

    if create_post_message_method:
      create_post_message_method(mail_message)
    else:
      if not use_activity:
        context.activate(activity='SQLQueue').sendMailHostMessage(mail_message)

if use_activity:
  method_kw = dict(event_relative_url=context.getRelativeUrl(),
                   from_url=from_url)
  if extra_header_dict:
    method_kw['extra_header_dict'] = extra_header_dict
  tag = script.id + '_reindex_' + context.getPath()
  context.reindexObject(activate_kw={'tag': tag})
  context.activate(after_tag=tag).MailMessage_sendByActivity(
    method_kw=method_kw, **kw)

if download:
  return mail_message
