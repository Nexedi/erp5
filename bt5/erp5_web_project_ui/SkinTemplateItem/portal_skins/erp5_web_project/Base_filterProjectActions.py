filtered_actions = {}
standard_view_action_list = []
for action_category_name, action_list in actions.items():
  if (action_category_name == 'object_view'):
    # This is needed because we want to merge maybe-existing actions from `project_view`.
    # In other words, this makes the script order-insensitive
    if action_category_name not in filtered_actions:
      filtered_actions[action_category_name] = []
    filtered_actions[action_category_name].extend([action for action in action_list if 'project_view' in action['id']])
    standard_view_action_list = [action for action in action_list if action['id'] == 'view']
  elif (action_category_name == 'object_jio_action'):
    filtered_actions[action_category_name] = [action for action in action_list if action['id'] not in ['post_query']]
  elif (action_category_name == 'project_view'):
    # Merged into object_view only: nothing consumes a project_view category client side
    if 'object_view' not in filtered_actions:
      filtered_actions['object_view'] = []
    filtered_actions['object_view'].extend(action_list)
  elif (action_category_name == 'object_jio_jump'):
    filtered_actions[action_category_name] = [action for action in action_list if action['id'] not in ['jump_to_portal_type']]
  else:
    filtered_actions[action_category_name] = action_list
if filtered_actions.get('object_view'):
  renamed_action_list = []
  renamed_action_id_set = set()
  for action in filtered_actions['object_view']:
    if action['id'] == 'project_view':
      # Rename the webapp default view action to 'view', to be compatible with the
      # Base_redirect calls hardcoding the 'view' action and with the panel highlight
      action = action.copy()
      action['id'] = 'view'
    if action['id'] not in renamed_action_id_set:
      renamed_action_id_set.add(action['id'])
      renamed_action_list.append(action)
  filtered_actions['object_view'] = renamed_action_list
elif standard_view_action_list:
  # A portal type contributing no project_view action keeps the standard view action
  filtered_actions['object_view'] = standard_view_action_list
return filtered_actions
