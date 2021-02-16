"""
send the username mail
"""
portal = context.getPortalObject()

person_list = context.getDestinationDecisionValueList(portal_type="Person")
login_list = []
for person in person_list:
  for login in person.objectValues(portal_type='ERP5 Login'):
    if login.getValidationState() == 'validated':
      login_list.append(login)

usernames = ' '.join(login.getReference() for login in login_list)

if context.hasDocumentReference():
  message_reference = context.getDocumentReference()
else:
  message_reference = portal.portal_preferences.getPreferredCredentialUsernameRecoveryMessageReference()
if message_reference is None:
  raise ValueError("Preference not configured")

notification_message = portal.NotificationTool_getDocumentValue(message_reference,
                                                                context.getLanguage())
mapping_dict = {
  "usernames" : usernames,
  }

if notification_message.getContentType() == "text/html":
  mail_text = notification_message.asEntireHTML(substitution_method_parameter_dict={'mapping_dict':mapping_dict})
else:
  mail_text = notification_message.asText(substitution_method_parameter_dict={'mapping_dict':mapping_dict})

subject = notification_message.asSubjectText(substitution_method_parameter_dict={'mapping_dict':mapping_dict})

portal.portal_notifications.sendMessage(
  recipient=person_list,
  subject=subject,
  message=mail_text,
  message_text_format=notification_message.getContentType(),
  notifier_list=('Mail Message',),
  store_as_event=portal.portal_preferences.isPreferredStoreEvents(),
  event_keyword_argument_dict={'follow_up':context.getRelativeUrl()},
)
