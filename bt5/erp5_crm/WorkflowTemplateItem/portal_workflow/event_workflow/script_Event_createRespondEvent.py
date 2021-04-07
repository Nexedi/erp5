# this script allows to create a new respond event for
# the current event and send message immediately.
portal = state_change.getPortal()
portal_workflow = portal.portal_workflow
event = state_change['object']

portal_type = portal_workflow.getInfoFor(event,
                                         'respond_event_portal_type',
                                         wf_id='event_workflow')

# Pass Mark Responded transition.
if not portal_type:
  return

title = portal_workflow.getInfoFor(event,
                                   'respond_event_title',
                                   wf_id='event_workflow')
resource = portal_workflow.getInfoFor(event,
                                      'respond_event_resource',
                                      wf_id='event_workflow')
text_content = portal_workflow.getInfoFor(event,
                                          'respond_event_text_content',
                                          wf_id='event_workflow')

event.Event_createRespondEvent(portal_type, title, resource, text_content)
