filtered_actions = {}
for action_category_name, action_list in actions.items():
  if (action_category_name == 'object_view'):
    filtered_actions[action_category_name] = [action for action in action_list if action['id'] in ['project_view']]
  elif (action_category_name == 'object_jio_action'):
    filtered_actions[action_category_name] = [action for action in action_list if action['id'] not in ['post_query']]
  else:
    filtered_actions[action_category_name] = action_list
return filtered_actions
