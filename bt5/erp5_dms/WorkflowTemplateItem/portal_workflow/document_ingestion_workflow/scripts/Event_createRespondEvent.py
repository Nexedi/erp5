# this script allows to create a new respond event for
# the current event

event = state_change['object']
respond_event_portal_type = None

history = event.portal_workflow.getInfoFor(event, 'history', wf_id='event_workflow')

for history_item in history[::-1]:
  if history_item['action'] == 'respond_action':
    respond_event_portal_type = history_item['respond_event_portal_type']
    respond_event_title = history_item['respond_event_title']
    respond_event_description = history_item['respond_event_description']
    break

if respond_event_portal_type is not None:
  event.Event_createRespondEvent(respond_event_portal_type,
                                 respond_event_title,
                                 respond_event_description)
