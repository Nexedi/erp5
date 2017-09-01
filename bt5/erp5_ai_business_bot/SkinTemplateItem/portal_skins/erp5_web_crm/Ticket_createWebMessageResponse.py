"""
Create a response web message event from ticket
"""
portal = context.getPortalObject()
current_object = context.getObject()
portal_type='Web Message'
translateString = portal.Base_translateString
module = portal.getDefaultModule(portal_type)

if not portal.Base_checkPermission(module.getId(), "Add portal content"):
  return context.Base_redirect(
    form_id,
    keep_items=dict(
      portal_status_message=translateString(
        "You do not have permission to add new event.")
      )
    )

# Create a new event
response = module.newContent(
  portal_type=portal_type,
  source=current_object.getDestination(),
  destination=current_object.getSourceList(),
  direction=direction,
  resource=resource,
  title='Re: ' + current_object.getTitle(),
  text_content=text_content,
  start_date=current_object.getStartDate(),
  # follow_up=current_object,
  # content_type=portal.portal_preferences.getPreferredTextEditor() and 'text/html' or 'text/plain'
  # subject_list=current_object.getSubjectList()
)

response.setFollowUpValueList([current_object])

if notification_message:
  response.Event_setTextContentFromNotificationMessage(
    reference=notification_message,
    substitution_method_parameter_dict=dict(
      reply_body='',
      reply_subject=title or ''
    )
  )

'''
if workflow_action:
  portal.portal_workflow.doActionFor(
    context,
    workflow_action,
  )
'''

message = translateString(
  "Created and associated a new ${ticket_type} for the Web Message.  Here is a recommended response.", 
  mapping=dict(ticket_type = translateString(ticket_type))
)

# Trigger appropriate workflow action
if not keep_draft:
  if direction == 'incoming':
    # Support event_workflow and event_simulation_workflow
    if portal.portal_workflow.isTransitionPossible(response, 'receive'):
      response.receive()
    if portal.portal_workflow.isTransitionPossible(response, 'stop'):
      response.stop()
  else:
    response.plan()

return response.Base_redirect('Ticket_viewWebMessageResponseDialog', keep_items={'portal_status_message': message})
#return response.Base_redirect('view', keep_items={'portal_status_message': message})
