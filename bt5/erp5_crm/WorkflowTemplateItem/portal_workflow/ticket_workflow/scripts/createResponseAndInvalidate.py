ticket = sci['object']
kw = sci['kwargs']

event = ticket.Ticket_getCausalityValue()
event.Event_createResponse(
  response_event_portal_type=kw['response_event_portal_type'],
  response_event_resource=kw['response_event_resource'],
  response_event_title=kw.get('response_event_title'),
  response_event_text_content=kw.get('response_event_text_content'),
  response_event_start_date=kw['response_event_start_date'],
  response_workflow_action=kw['response_workflow_action'],
  response_event_notification_message=kw['response_event_notification_message'],
  default_destination=kw['default_destination'],
  response_event_content_type=kw['response_event_content_type'])

ticket.invalidate()
