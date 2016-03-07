request = container.REQUEST
if request.get('dialog_action_url'):
  current_url = request['dialog_action_url']
  for action in dialog_actions:
    if current_url == action['original_url']:
      return action
else:
  for action in dialog_actions:
    if current_url == action['url'].split('?')[0]:
      return action
# still not found, return the first action with form_id matching
form_id = current_url.split('/')[-1]
for action in dialog_actions:
  if form_id == action['url'].split('?')[0].split('/')[-1]:
    return action
return None
