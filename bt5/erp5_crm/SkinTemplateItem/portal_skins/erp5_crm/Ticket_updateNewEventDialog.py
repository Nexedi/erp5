"""Preview the response from notification message for ticket create response dialog.
"""
if notification_message:
  temp_event = context.getPortalObject().event_module.newContent(
    temp_object=True,
    portal_type=portal_type,
    source=source,
    destination=destination,
    follow_up_value=context,
    resource=resource,
    language=context.getLanguage(),
    content_type=content_type)

  try:
    title_field_id = 'your_title'
    field = getattr(context, dialog_id)[title_field_id]
    original_title = field.getFieldValue(title_field_id, 'default')[0](field, title_field_id)
  except (AttributeError, KeyError):
    original_title = ''
  temp_event.Event_setTextContentFromNotificationMessage(
     reference=notification_message,
     substitution_method_parameter_dict=dict(
       reply_body='',
       reply_subject=original_title))
  title = temp_event.getTitle().strip()

  if original_title and original_title not in title:
    title = '%s (%s)' % (title, original_title)

return context.Base_renderForm(dialog_id, keep_items={
  'your_notification_message': '',
  'your_title': temp_event.getTitle(),
  'your_text_content': temp_event.getTextContent(),
  'your_content_type': temp_event.getContentType(),
  'your_resource': temp_event.getResource()
})
