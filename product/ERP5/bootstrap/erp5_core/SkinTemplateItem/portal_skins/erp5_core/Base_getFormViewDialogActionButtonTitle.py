request = context.REQUEST

button_title = request.get('button_title', None)
if button_title is not None:
  return button_title

wf_actions =  context.portal_actions.portal_actions.listFilteredActionsFor(context)['workflow']
workflow_action = request.get('workflow_action', None) or request.get('field_my_workflow_action', None)
if workflow_action:
  for action in wf_actions:
    if action['id'] == workflow_action:
      return action['name']

if workflow_action:
  # It means that workflow_action is not available now. Redirect to default view with a nice message.
  from Products.ERP5Type.Message import translateString
  message = translateString("Workflow state may have been updated by other user. Please try again.")
  context.Base_redirect('view', keep_items={'portal_status_message': message})

if form.action_title:
  return form.action_title

return form.title
