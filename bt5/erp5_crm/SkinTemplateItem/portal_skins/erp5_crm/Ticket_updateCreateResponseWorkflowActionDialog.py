"""Preview the response from notification message for ticket create response dialog.
"""
event = context.Ticket_getCausalityValue()

if response_event_notification_message:
  temp_event = context.getPortalObject().event_module.newContent(
    temp_object=True,
    portal_type=response_event_portal_type,
    source=default_destination or context.getDestination(),
    destination=event.getSource(),
    causality_value=event,
    follow_up_list=event.getFollowUpList(),
    resource=response_event_resource,
    language=event.getLanguage(),
    content_type=response_event_content_type or event.getContentType())

  try:
    title_field_id = 'your_response_event_title'
    field = getattr(context, dialog_id)[title_field_id]
    original_title = field.getFieldValue(title_field_id, 'default')[0](field, title_field_id)
  except (AttributeError, KeyError):
    original_title = ''
  if original_title:
    reply_subject = original_title
  else:
    reply_subject = event.getReplySubject()
  temp_event.Event_setTextContentFromNotificationMessage(
     reference=response_event_notification_message,
     substitution_method_parameter_dict=dict(
       reply_body=event.getReplyBody(),
       reply_subject=reply_subject))
  title = temp_event.getTitle()
  if reply_subject not in title:
    title = '%s (%s)' % (title, reply_subject)

  # XXX this relies on formulator internals, we force the variables in request and
  # re-render the form.
  request = container.REQUEST
  request.set('your_response_event_notification_message', '')
  request.set('your_response_event_title', title)
  request.set('your_response_event_text_content', temp_event.getTextContent())
  request.set('your_response_event_content_type', temp_event.getContentType())
  request.set('your_response_event_resource', temp_event.getResource())
  # for new UI
  request.form['your_response_event_notification_message'] = ''
  request.form['your_response_event_title'] = title
  request.form['your_response_event_text_content'] = temp_event.getTextContent()
  request.form['your_response_event_content_type'] = temp_event.getContentType()
  request.form['your_response_event_resource'] = temp_event.getResource()

return context.Base_renderForm('Ticket_viewCreateResponseWorkflowActionDialog')
