"""
send the password reset link by mail
"""
portal = context.getPortalObject()

person = context.getDestinationDecisionValue(portal_type="Person")
reference = context.getReference()
if context.hasDocumentReference():
  message_reference = context.getDocumentReference()
else:
  message_reference = portal.portal_preferences.getPreferredCredentialPasswordRecoveryMessageReference()
if message_reference is None:
  raise ValueError, "Preference not configured"
notification_message = portal.NotificationTool_getDocumentValue(message_reference,
                                                                context.getLanguage())

context.REQUEST.set('came_from', context.getUrlString())

if context.hasStopDate():
  kw = {'expiration_date':context.getStopDate()}
else:
  kw = {}

portal.portal_password.mailPasswordResetRequest(user_login=reference,
                                                REQUEST=context.REQUEST,
                                                notification_message=notification_message,
                                                store_as_event=portal.portal_preferences.isPreferredStoreEvents(),
                                                **kw)
