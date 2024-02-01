if body is None:
  body = context.getTextContent() #XXX This does not support structured text format.

# Subject
if subject is None:
  subject = context.getTitle()

# From
if from_url is None:
  sender = context.getSourceValue()
  if sender is not None:
    if sender.hasTitle():
      from_url = '"%s" <%s>' % (sender.getTitle(),
                            sender.getDefaultEmailText())
    else:
      from_url = sender.getDefaultEmailText()
  else:
    user = context.portal_membership.getAuthenticatedMember().getUserName()
    from_url = '"%s" <%s>' % (user,
                              context.email_from_address)
# Return-Path. TODO: this is not implemented
if reply_url is None:
  reply_url = context.portal_preferences.getPreferredEventSenderEmail()
additional_headers = None  # pylint: disable=unused-variable
if reply_url:
  additional_headers = {'Return-Path':reply_url}

# To (multiple)
recipient_list = context.BugLine_getRecipientValueList()
to_url_list = []
if to_url is None:
  for recipient in recipient_list:
    email = recipient.getDefaultEmailText()
    if email:
      if recipient.hasTitle():
        to_url_list.append('"%s" <%s>' % (recipient.getTitle(), email))
      else:
        to_url_list.append(email)
    else:
      raise ValueError('Recipient %s has no defined email' % recipient)
elif same_type(to_url, ''):
  to_url_list.append(to_url)

# Attachments
if attachment_list is None:
  attachment_list = []
for attachment in context.getAggregateValueList():
  mime_type, content = attachment.getMimeTypeAndContent()
  name = attachment.getReference()

  attachment_list.append({'mime_type':mime_type,
                          'content':content,
                          'name':name})

# Build message per destination
mail_message = None
if context.getContentType() == 'text/html':
  mail_template = context.Event_viewHtmlMimeMessage
else:
  mail_template = context.Event_viewMimeMessage

for to_url in to_url_list:
  multipart = mail_template.as_message(mfrom=from_url,
                                       mto=to_url,
                                       subject=subject,
                                       body=body,
                                       encoding='utf-8')
  for attachment_dict in attachment_list:
    multipart.add_file(data=attachment_dict['content'],
                       content_type=attachment_dict['mime_type'],
                       filename=attachment_dict['name'])
  mail_message = bytes(multipart)
  # Bug Message not send email it self.
  #context.activate(activity='SQLQueue').sendMailHostMessage(mail_message)

context.setData(mail_message)
context.deliver()

if download:
  return mail_message
