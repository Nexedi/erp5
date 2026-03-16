filtered_actions = {}
for action_category_name, action_list in actions.items():
  if (action_category_name == 'object_view'):
    filtered_actions[action_category_name] = [action for action in action_list if 'project_view' in action['id'] ]
  elif (action_category_name == 'object_jio_action'):
    filtered_actions[action_category_name] = [action for action in action_list if action['id'] not in ['post_query']]
  elif (action_category_name == 'object_jio_jump'):
    filtered_actions[action_category_name] = [action for action in action_list if action['id'] not in ['jump_to_portal_type']]
  else:
    filtered_actions[action_category_name] = action_list

# Ensure project_view actions are handled after dict iteration
if 'project_view' in filtered_actions:
  filtered_actions['object_view'] = filtered_actions['project_view']

return filtered_actions
