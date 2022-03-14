# this script allows to create a new related event quickly

portal = state_change.getPortal()
portal_workflow = portal.portal_workflow
event = state_change['object']

title = portal_workflow.getInfoFor(event,
                                   'related_event_title',
                                   wf_id='event_workflow')

description = portal_workflow.getInfoFor(event,
                                         'related_event_description',
                                         wf_id='event_workflow')

portal_type = portal_workflow.getInfoFor(event,
                                         'related_event_portal_type',
                                         wf_id='event_workflow')

event.Event_createRelatedEvent(portal_type, title, description)
