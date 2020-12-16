from email.utils import formataddr
portal = context.getPortalObject()
event = portal.restrictedTraverse(event_relative_url)

subject = event.getTitle()
body = event.getTextContent()
sender = event.getSourceValue()
if kw.get("from_url") is not None:
  from_url = kw.get("from_url")
elif sender is not None:
  from_url = formataddr((sender.hasTitle() and sender.getTitle(), sender.getDefaultEmailText()))
else:
  from_url = portal.portal_preferences.getPreferredEventSenderEmail()

to_url = formataddr((context.hasTitle() and context.getTitle(), context.getDefaultEmailText()))

document_type_list = list(event.getPortalEmbeddedDocumentTypeList()) + list(event.getPortalDocumentTypeList())
embedded_file_list = event.getAggregateValueList(portal_type=document_type_list)

extra_header_dict = kw.get('extra_header_dict') or {}

content_type = event.getContentType()
mail_message = portal.Base_createMailMessageAsString(
  from_url,
  to_url,
  subject,
  body,
  content_type,
  embedded_file_list=embedded_file_list,
  extra_header_dict=extra_header_dict)

create_post_message_method = event.getTypeBasedMethod('createPostMessage')
if create_post_message_method is not None:
  create_post_message_method(mail_message)
else:
  # We do not want to retry those activities, as sending email is not transactional safe
  event.activate(
    activity='SQLQueue',
    conflict_retry=False,
    max_retry=0
  ).sendMailHostMessage(mail_message)
