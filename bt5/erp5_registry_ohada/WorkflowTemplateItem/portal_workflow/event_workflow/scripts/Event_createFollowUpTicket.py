# this script allows to create a new follow up ticket for
# the current event if the event isn't already linked with
# an existing ticket

event = state_change['object']

if not(len(event.getFollowUpValueList())):
  history = event.portal_workflow.getInfoFor(event, 'history', wf_id='event_workflow')

  for history_item in history[::-1]:
    if history_item['action'] == 'assign_action':
      follow_up_ticket_type = history_item['follow_up_ticket_type']
      follow_up_ticket_title = history_item['follow_up_ticket_title']
      break

  event.Event_createFollowUpTicket(follow_up_ticket_title, follow_up_ticket_type)
