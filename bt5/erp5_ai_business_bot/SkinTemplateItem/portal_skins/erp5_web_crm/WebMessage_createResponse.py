"""
  This script creates a new event with given metadata and
  attaches it to the current ticket.
"""


portal = context.getPortalObject()
translateString = portal.Base_translateString
module = portal.getDefaultModule(portal_type)

if portal_type not in module.getVisibleAllowedContentTypeList():
  return context.Base_redirect(form_id,
                               keep_items=dict(
       portal_status_message=translateString("You do not have permission to add new event.")))
  
# Create a new event
event = module.newContent(portal_type=portal_type, 
                          title=title,
                          text_content=text_content,
                          content_type=portal.portal_preferences.getPreferredTextEditor() and 'text/html' or 'text/plain',
                          resource=resource,
                          source=source,
                          destination=destination,
                          start_date=DateTime(),
                          follow_up=context.getRelativeUrl())

# Trigger appropriate workflow action
if not keep_draft:
  if direction == 'incoming':
    # Support event_workflow and event_simulation_workflow
    if portal.portal_workflow.isTransitionPossible(event, 'receive'):
      event.receive()
    if portal.portal_workflow.isTransitionPossible(event, 'stop'):
      event.stop()
  else:
    event.plan()

# Redirect to event
portal_status_message = translateString(
  "Created and associated a new ${portal_type} to the ticket.", 
  mapping=dict(portal_type = translateString(portal_type)))
return event.Base_redirect('view', keep_items = dict(portal_status_message=portal_status_message), **kw)
