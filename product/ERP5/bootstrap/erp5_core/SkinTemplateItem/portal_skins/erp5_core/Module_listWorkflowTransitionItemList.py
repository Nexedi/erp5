result = {
  # items (ready to be used in a listfield items) of common workflow transition on a module's documents
  'transition_item_list': [],
  # form id for each transition
  'form_id_dict': {},
  # additional catalog parameter per transition
  'listbox_parameter_dict': {}
}

TRIGGER_USER_ACTION = 1

portal = context.getPortalObject()
module = context
type_tool = portal.portal_types
workflow_tool = portal.portal_workflow
translate = portal.Base_translateString

module_portal_type = type_tool.getTypeInfo(module)

checked_workflow_id_dict = {}
for document_portal_type_id in module_portal_type.getTypeAllowedContentTypeList():
  if (filter_portal_type_list is not None) and (filter_portal_type_list not in portal_type_list):
    continue
  for workflow in workflow_tool.getWorkflowsFor(document_portal_type_id):
    if workflow.id not in checked_workflow_id_dict:
      # Do not check the same workflow twice
      checked_workflow_id_dict[workflow.id] = None

      state_variable = workflow.state_var

      allowed_state_dict = {}

      if getattr(workflow, 'states', None) is not None:
        for state_id, state in workflow.states.items():
          for possible_transition_id in state.transitions:
            if possible_transition_id in allowed_state_dict:
              allowed_state_dict[possible_transition_id].append(state_id)
            else:
              allowed_state_dict[possible_transition_id] = [state_id]
        for transition_id in allowed_state_dict:
          transition = workflow.transitions.get(transition_id, None)
          if transition is None:
            continue
          # Only display user action transition with a dialog to show to user
          if (transition.trigger_type == TRIGGER_USER_ACTION) and (transition.actbox_url) and (transition.actbox_name):
            action_form_id = transition.actbox_url.rsplit('/', 1)[1].split('?')[0]

            result['transition_item_list'].append((translate(transition.actbox_name), transition_id))
            result['form_id_dict'][transition_id] = action_form_id
            # XXX portal_type parameter must also probably be added too
            # This would required to detect identical transition id for different workflow
            result['listbox_parameter_dict'][transition_id] = [(state_variable, allowed_state_dict[transition_id])]
          elif (transition.trigger_type == TRIGGER_USER_ACTION) and (transition_id == 'delete_action'):
            result['listbox_parameter_dict'][transition_id] = [(state_variable, allowed_state_dict[transition_id])]

result['transition_item_list'].sort()
result['transition_item_list'].insert(0, ('', ''))

return result
