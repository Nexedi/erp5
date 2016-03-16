# Return the current action to know which tab is selected

for action in actions.get('object_view', []):
  if current_url == action['url'].split('?')[0]:
    return action
