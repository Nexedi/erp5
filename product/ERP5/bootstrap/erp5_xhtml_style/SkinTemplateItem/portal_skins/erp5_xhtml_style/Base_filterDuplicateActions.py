"""This script filters duplicate actions for a document.
Duplicate actions are actions with the same ID in the same action category.
In case of duplicate, only the first action will be kept.

`actions` is the mapping returned by ActionsTool.listFilteredActionsFor
The script must be called on the context of the document.
"""
def filterDuplicateActions(actions):
  new_actions = {}

  for action_category, action_list in list(actions.items()):
    if action_category == 'object_onlyxhtml_view':
      action_category = 'object_view'

    new_actions.setdefault(action_category, [])
    existing_actions = set([x['id'] for x in new_actions[action_category]])
    keep_action = new_actions[action_category].append

    for action in action_list:
      if action['id'] not in existing_actions:
        existing_actions.add(action['id'])
        keep_action(action)
    if (action_category == 'object_view'):
      new_actions[action_category].sort(key=lambda x: x.get('priority', 1.0))

  return new_actions

if getattr(context, 'getPortalType', None) is not None:
  return filterDuplicateActions(actions)
return actions
