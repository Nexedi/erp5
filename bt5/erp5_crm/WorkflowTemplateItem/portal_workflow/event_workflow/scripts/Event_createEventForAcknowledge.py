# this script allows to create a new respond event for
# the current acknowledged event

portal = state_change.getPortal()
portal_workflow = portal.portal_workflow
event = state_change['object']

follow_up_ticket_type = portal_workflow.getInfoFor(event,
                                                   'follow_up_ticket_type',
                                                   wf_id='event_workflow')

follow_up_ticket_title = portal_workflow.getInfoFor(event,
                                                    'follow_up_ticket_title',
                                                    wf_id='event_workflow')

create_event = portal_workflow.getInfoFor(event, 'create_event',
                                          wf_id='event_workflow')

quote_original_message = portal_workflow.getInfoFor(event,
                                                    'quote_original_message',
                                                    wf_id='event_workflow')

follow_up = event.getFollowUp()

if follow_up is None:
  if not (follow_up_ticket_type and follow_up_ticket_title):
    raise ValueError('Follow up must not empty when assign or acknowledge.')

if follow_up is None and follow_up_ticket_type and follow_up_ticket_title:
  event.Event_createFollowUpTicket(follow_up_ticket_title,
                                   follow_up_ticket_type)

if create_event:
  new_event = portal.event_module.newContent(portal_type=event.portal_type,
                                             destination=event.getSource(),
                                             follow_up=event.getFollowUp(),
                                             causality=event.getRelativeUrl(),
                                             start_date=DateTime())

  if quote_original_message:
    new_event.edit(content_type=event.getContentType(),
                   title=event.getReplySubject(),
                   text_content=event.getReplyBody())
