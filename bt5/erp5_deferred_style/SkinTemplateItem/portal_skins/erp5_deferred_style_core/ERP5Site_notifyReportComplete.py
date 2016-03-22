portal = context.getPortalObject()

portal.portal_notifications.activate(activity='SQLQueue').sendMessage(
  recipient=user_name,
  subject=subject,
  message=message,
  message_text_format='text/plain',
  notifier_list=('Mail Message',),
  store_as_event=False,
  attachment_list=attachment_list,
)
