portal = context.getPortalObject()

event_path = portal.restrictedTraverse(event_path)

follow_up = event_path.getParentRelativeUrl()
event_portal_type = event_path.getEventPortalType()
resource_reference = event_path.getResourceReference()
source = event_path.getSource()

language = context.getLanguage()
if not language:
  language = portal.portal_preferences.getPreferredCustomerRelationLanguage()
notification_message = portal.notification_message_module.NotificationTool_getDocumentValue(
  resource_reference,
  language=language)
assert notification_message is not None, "%s not found." % resource_reference

context.Base_addEvent(title='',
  direction='outgoing',
  portal_type=event_portal_type,
  resource=notification_message.getSpecialise(),
  notification_message=resource_reference,
  keep_draft=keep_draft,
  follow_up=follow_up,
  source=source,
  language=language,
  batch_mode=True)
