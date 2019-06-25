portal = context.getPortalObject()
if not language:
  language = context.getLanguage()
  if not language:
    language = portal.portal_preferences.getPreferredCustomerRelationLanguage()

notification_message = portal.portal_notifications.getDocumentValue(
                                language=language,
                                reference=reference)

if substitution_method_parameter_dict is None:
  substitution_method_parameter_dict = {}
# Notification method will receive the current event under "event_value" key.
# This way notification method can return properties from recipient or follow up of the event.
substitution_method_parameter_dict.setdefault('event_value', context)


if notification_message is not None:
  context.setContentType(notification_message.getContentType())
  target_format = "txt"
  if context.getContentType() == 'text/html':
    target_format = "html"
  mime, text_content = notification_message.convert(target_format,
      substitution_method_parameter_dict=substitution_method_parameter_dict)
  context.setTextContent(text_content)
  context.setAggregateSet(
      context.getAggregateList() + notification_message.getProperty('aggregate_list', []))

  if not context.hasTitle():
    context.setTitle(notification_message.asSubjectText(
      substitution_method_parameter_dict=substitution_method_parameter_dict))
