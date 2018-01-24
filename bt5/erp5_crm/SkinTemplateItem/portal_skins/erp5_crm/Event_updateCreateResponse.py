"""Preview the response from notification message for event create response dialog.
"""
if response_event_notification_message:
  temp_event = context.getPortalObject().event_module.newContent(
    temp_object=True,
    portal_type=response_event_portal_type,
    source=default_destination or context.getDestination(),
    destination=context.getSource(),
    causality_value=context,
    follow_up_list=context.getFollowUpList(),
    resource=response_event_resource,
    language=context.getLanguage(),
    content_type=response_event_content_type or context.getContentType())

  temp_event.Event_setTextContentFromNotificationMessage(
     reference=response_event_notification_message,
     substitution_method_parameter_dict=dict(reply_body=context.getReplyBody(),
                                             reply_subject=context.getReplySubject()))
                                             
  # XXX this relies on formulator internals, we force the variables in request and
  # re-render the form.
  request = container.REQUEST
  request.form['your_response_event_notification_message'] = ''
  request.form['your_response_event_title'] = temp_event.getTitle()
  request.form['your_response_event_text_content'] = temp_event.getTextContent()
  request.form['your_response_event_resource'] = temp_event.getResource()

return context.Base_renderForm('Event_viewCreateResponseDialog')
