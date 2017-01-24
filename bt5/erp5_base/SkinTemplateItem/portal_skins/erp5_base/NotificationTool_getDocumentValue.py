portal = context.getPortalObject()
notification_message_list = portal.portal_catalog.getDocumentValueList(
  portal_type='Notification Message',
  validation_state=validation_state or 'validated',
  reference=reference,
  language=language,
  all_languages=True,
)
if notification_message_list:
  return notification_message_list[0].getObject()
