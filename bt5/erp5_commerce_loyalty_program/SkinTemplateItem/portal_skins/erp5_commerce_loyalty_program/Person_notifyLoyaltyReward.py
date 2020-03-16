notification_message_reference = context.portal_preferences.getPreferredLoyaltyRewardNotificationMessageReference()
if notification_message_reference and context.getDefaultEmailText():

  notification_message = context.NotificationTool_getDocumentValue(context.portal_preferences.getPreferredLoyaltyRewardNotificationMessageReference(), context.Localizer.get_selected_language())
  if notification_message is None:
    raise ValueError, 'Unable to found Notification Message with reference "%s".' % notification_message_reference


  if notification_message:
    notification_mapping_dict = {'first_name': context.getFirstName(),
                                 'last_name': context.getLastName(),
                                 'price': context.portal_preferences.getPreferredLoyaltyRewardPrice()
                                }

    # Preserve HTML else convert to text
    if notification_message.getContentType() == "text/html":
      mail_text = notification_message.asEntireHTML(
        substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})
    else:
      mail_text = notification_message.asText(
        substitution_method_parameter_dict={'mapping_dict':notification_mapping_dict})

    # Send email
    context.portal_notifications.sendMessage(
      sender=None,
      recipient=context,
      subject="%s" % (notification_message.getTitle()),
      message=mail_text,
      message_text_format=notification_message.getContentType(),
      store_as_event=True,
      event_keyword_argument_dict={'follow_up': loyalty})
