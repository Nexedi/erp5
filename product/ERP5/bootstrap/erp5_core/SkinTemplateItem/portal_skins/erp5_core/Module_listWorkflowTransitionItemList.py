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
  if (filter_portal_type_list is not None) and (document_portal_type_id not in filter_portal_type_list):
    continue
  for workflow in workflow_tool.getWorkflowValueListFor(document_portal_type_id):
    workflow_id = workflow.getId()
    if workflow_id not in checked_workflow_id_dict:
      # Do not check the same workflow twice
      checked_workflow_id_dict[workflow_id] = None

      state_variable = workflow.getStateVariable()

      allowed_state_dict = {}

      state_value_list = workflow.getStateValueList()
      if state_value_list:
        for state in state_value_list:
          state_reference = state.getReference()
          for possible_transition in state.getDestinationValueList():
            if possible_transition in allowed_state_dict:
              allowed_state_dict[possible_transition].append(state_reference)
            else:
              allowed_state_dict[possible_transition] = [state_reference]
        for transition in allowed_state_dict:
          transition_reference = transition.getReference()
          # Only display user action transition with a dialog to show to user
          if transition.getTriggerType() == TRIGGER_USER_ACTION and transition.getAction() and transition.getActionName():
            action_form_id = transition.getAction().rsplit('/', 1)[1].split('?')[0]

            result['transition_item_list'].append((translate(transition.getActionName()), transition_reference))
            result['form_id_dict'][transition_reference] = action_form_id
            # XXX portal_type parameter must also probably be added too
            # This would required to detect identical transition id for different workflow
            result['listbox_parameter_dict'][transition_reference] = [(state_variable, allowed_state_dict[transition])]
          elif transition.getTriggerType() == TRIGGER_USER_ACTION and transition_reference == 'delete_action':
            result['listbox_parameter_dict'][transition_reference] = [(state_variable, allowed_state_dict[transition])]

result['transition_item_list'].sort()
result['transition_item_list'].insert(0, ('', ''))

return result
