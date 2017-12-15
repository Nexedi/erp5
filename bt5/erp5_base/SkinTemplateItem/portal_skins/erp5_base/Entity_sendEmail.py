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

internet_message_post_module = portal.getDefaultModuleValue('Internet Message Post', None)
if internet_message_post_module is not None:
  # erp5_interface_post is installed, so it is needed to track outgoing emails
  internet_message_post = internet_message_post_module.newContent(
    portal_type='Internet Message Post',
    title="Internet Message for %s" % event.getTitle(),
    reference=event.getReference(),
    data=mail_message,
  )
  internet_message_post.allowExport()
  event_aggregate_list = event.getAggregateList()
  event_aggregate_list.append(internet_message_post.getRelativeUrl())
  event.setAggregateList(event_aggregate_list)
else:
  event.sendMailHostMessage(mail_message)
