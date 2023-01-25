"""
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString
module = portal.getDefaultModule(portal_type)

if not portal.Base_checkPermission(module.getId(), "Add portal content"):
  return context.Base_redirect(form_id,
                               keep_items=dict(
     portal_status_message=translateString("You do not have permission to add new event.")))

# Create a new event
response = module.newContent(portal_type=portal_type,
                             source=source,
                             destination=destination,
                             resource=resource,
                             title=title,
                             text_content=text_content,
                             start_date=start_date,
                             follow_up_value=context,
                             content_type=content_type)

if attachment_file:
  document = response.Base_contribute(
    batch_mode=True,
    redirect_to_document=False,
    use_context_for_container=True,
    portal_type='Embedded File',
    file=attachment_file,
  )
  response.setAggregateValue(document)

if notification_message:
  response.Event_setTextContentFromNotificationMessage(
    reference=notification_message
  )

if workflow_action:
  portal.portal_workflow.doActionFor(
    context,
    workflow_action,
  )

message = translateString(
  "Created and associated a new ${portal_type} to the ticket.",
  mapping=dict(portal_type = translateString(portal_type)))

if event_workflow_action == 'send':
  response.start()
elif event_workflow_action == 'plan':
  response.plan()
elif event_workflow_action == 'deliver':
  response.deliver()
elif event_workflow_action == 'draft':
  pass
else:
  raise NotImplementedError('Do not know what to do')
return response.Base_redirect('view', keep_items={'portal_status_message': message})
