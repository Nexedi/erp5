"""This script filters duplicate actions for a document.
Duplicate actions are actions with the same ID in the same action category.
In case of duplicate, only the first action will be kept.

`actions` is the mapping returned by ActionsTool.listFilteredActionsFor
The script must be called on the context of the document.
"""
from Products.ERP5Type.Cache import CachingMethod
def filterDuplicateActions(actions):
  new_actions = {}

  for action_category, action_list in actions.items():
    existing_actions = set()
    new_actions[action_category] = []
    keep_action = new_actions[action_category].append

    for action in action_list:
      if action['id'] not in existing_actions:
        existing_actions.add(action['id'])
        keep_action(action)
  return new_actions


def hasDuplicateActions(portal_type, user_name):
  len_actions = 0
  len_filtered_actions = 0
  for cat in actions.values():
    len_actions += len(cat)
  filtered_actions = filterDuplicateActions(actions)
  for cat in filtered_actions.values():
    len_filtered_actions += len(cat)
  return len_actions != len_filtered_actions


hasDuplicateActions = CachingMethod(
                          hasDuplicateActions,
                          id='Base_filterDuplicateActions.hasDuplicateActions',
                          cache_factory='erp5_ui_long')

user_name = getattr(container.REQUEST, 'AUTHENTICATED_USER', '')

if getattr(context, 'getPortalType', None) is not None:
  if hasDuplicateActions(context.getPortalType(), user_name):
    return filterDuplicateActions(actions)
return actions
