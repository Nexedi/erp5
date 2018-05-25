form_id_dict = context.Module_listWorkflowTransitionItemList()['form_id_dict']

# During rendering, this variable has been set into the request
# Render what user selected
action = request.get("mass_workflow_action", "")
if action:
  return form_id_dict.get(action, '')

# Validate only if user didn't change the possible action
action = request.get("field_your_mass_workflow_action", "")
if (action and action == request.get("field_your_previous_mass_workflow_action", "")):
  return form_id_dict.get(action, '')

return ''
