filtered_actions = {}
for action_category_name, action_list in actions.items():
  filtered_actions[action_category_name] = [action for action in action_list if 'project_view' in action['id']]
return filtered_actions
