"""Send the permanent link by email"""
#TODO: Remove hardcoding
notification_message = context.NotificationTool_getDocumentValue(reference="cloudooo-document.share.link")

mapping_dict = {'link_url': context.Document_getPermanentUrl()}

#asText required auditor proxy
mail_text = notification_message.asText(
  substitution_method_parameter_dict={'mapping_dict':mapping_dict})


#We can not use portal_notifications.sendMessage, because we doesn't create person with email list
support_email = "no-reply@cloudooo.com"
message_title = notification_message.getTitle()
for email in recipient_email:
  context.Event_viewMimeMessage(
    mto=email,
    subject=message_title,
    mfrom=support_email,
    body=mail_text,
    encoding='utf-8'
  )

message = context.Base_translateString("Your document link was sended by email.")
context.Base_redirect('view',keep_items={'portal_status_message': message})
