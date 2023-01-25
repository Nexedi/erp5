"""
  Send an email after accept a credential request
  Proxy: Assignee, Assignor, Member -- allow to send notification by mail.
"""

portal = context.getPortalObject()
recipient = context.getDestinationDecisionValue(portal_type="Person")

#Define the type of notification
notification_type = "without-password"
if password:
  notification_type = "with-password"

#Get message from catalog
notification_reference = 'credential_request-confirmation-%s' % notification_type
notification_message = portal.portal_notifications.getDocumentValue(reference=notification_reference,
                                                                    language=recipient.getLanguage())
if notification_message is None:
  raise ValueError('Unable to found Notification Message with reference "%s".' % notification_reference)

#Set notification mapping
notification_mapping_dict = {'login_name': login}
if password:
  notification_mapping_dict.update(
                            {'login_password' : password})

#Preserve HTML else convert to text
if notification_message.getContentType() == "text/html":
  mail_text = notification_message.asEntireHTML(
    substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})
else:
  mail_text = notification_message.asText(
    substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})

#Send email
portal.portal_notifications.sendMessage(
  sender=None,
  recipient=recipient,
  subject=notification_message.getTitle(),
  message=mail_text,
  message_text_format=notification_message.getContentType(),
  notifier_list=(portal.portal_preferences.getPreferredLoginAndPasswordNotifier(),),
  store_as_event= portal.portal_preferences.isPreferredStoreEvents(),
  event_keyword_argument_dict={'follow_up':context.getRelativeUrl()},
  )
