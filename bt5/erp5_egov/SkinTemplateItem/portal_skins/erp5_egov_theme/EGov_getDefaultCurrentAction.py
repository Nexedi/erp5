if current_action is None:
 for action in actions:
    if action['id'] == 'view':
      current_action = action

return current_action
