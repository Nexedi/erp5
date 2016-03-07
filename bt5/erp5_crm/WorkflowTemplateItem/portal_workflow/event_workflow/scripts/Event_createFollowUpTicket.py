# this script allows to create a new follow up ticket for
# the current event if the event isn't already linked with
# an existing ticket

event = state_change['object']
portal = state_change.getPortal()
portal_workflow = portal.portal_workflow

follow_up_ticket_title = ''

if not(len(event.getFollowUpValueList())):

  follow_up_ticket_type = portal_workflow.getInfoFor(event,
                                                     'follow_up_ticket_type',
                                                     wf_id='event_workflow')

  follow_up_ticket_title = portal_workflow.getInfoFor(event,
                                                      'follow_up_ticket_title',
                                                      wf_id='event_workflow')

  event.Event_createFollowUpTicket(follow_up_ticket_title, follow_up_ticket_type)
