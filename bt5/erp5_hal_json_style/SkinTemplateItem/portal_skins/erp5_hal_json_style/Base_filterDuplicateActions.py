"""This script is MANDATORY to use to filter out duplicate/incompatible actions for a document.
Duplicate actions are actions with the same ID in the same action category or related XHTML category.
In case of duplicate, the JIO version (or the first in the same category) will be kept.

In the ideal state - this would return only categories named "object_action", "object_view" without
any infixes. This would remove logic from templates and the would not need to know about "_jio_"
actions and others possibly introduced in the future.

`actions` is the mapping returned by ActionsTool.listFilteredActionsFor
The script must be called on the context of the document.
"""
from Products.ERP5Type.Cache import CachingMethod


def filterActions(actions):
  """Reorganise and rename action categories for templates so they do not need to contain any logic."""
  filtered_actions = {}

  for action_category_name, action_list in actions.items():
    # action category _onlyjio_ contains actions shown only in RenderJS interface
    # we hide this detail from templates because they should not contain any logic
    if action_category_name == "object_onlyjio_view":
      # Do not merge the object_jio_view, which is used in officejs only
      # to generate the JSON export
      action_category_name = "object_view"
    elif "_onlyjio_" in action_category_name:
      action_category_name = action_category_name.replace("_onlyjio_", "_jio_")
    if action_category_name in filtered_actions:
      filtered_actions[action_category_name].extend(action_list)
    else:
      filtered_actions[action_category_name] = action_list
  return {action_category_name: sorted(action_list, key=lambda x: x.get('priority', 1.0))
          for action_category_name, action_list in filtered_actions.items()}


def filterDuplicateActions(actions):
  new_actions = {}

  for action_category_name, action_list in actions.items():

    new_actions.setdefault(action_category_name, {})

    # with introduction of the new UI some actions can have JIO only versions
    # so we have to consider them as duplicates even though they are in different
    # category because those categories are rendered together (e.g object_action and object_jio_action)
    is_jio_action_category = "_jio_" in action_category_name

    # we could if not is_jio_action_category: continue ...

    other_action_id_set = set()
    if is_jio_action_category:
      prefix, _, suffix = action_category_name.split("_", 2)  # omit the _jio_
      other_action_id_set.update(action['id']
        for action in actions.get(prefix + "_" + suffix, []))
    else:
      if "_" in action_category_name:
        prefix, suffix = action_category_name.split("_", 1)
        other_action_id_set.update(action['id']
          for action in actions.get(prefix + "_jio_" + suffix, []))

    for action in action_list:
      if not is_jio_action_category:  # prefer JIO version of the same action
        if action['id'] in other_action_id_set:
          continue
      if action['id'] not in new_actions[action_category_name]:
        new_actions[action_category_name][action['id']] = action

  # return dict[str: list] of category_name: sorted list of contained actions
  # global actions do not have priority so we give them 1.0 by default
  return {action_category_name: sorted(action_dict.values(), key=lambda x: x.get('priority', 1.0))
          for action_category_name, action_dict in new_actions.items()}


def hasJIODuplicateActions(portal_type, user_name):
  len_actions = 0
  len_filtered_actions = 0
  for cat in actions.values():
    len_actions += len(cat)
  filtered_actions = filterDuplicateActions(actions)
  for cat in filtered_actions.values():
    len_filtered_actions += len(cat)
  return len_actions != len_filtered_actions


hasDuplicateActions = CachingMethod(
                          hasJIODuplicateActions,
                          id='Base_filterDuplicateActions.hasJIODuplicateActions',
                          cache_factory='erp5_ui_long')

actions = filterActions(actions)
user_name = getattr(container.REQUEST, 'AUTHENTICATED_USER', '')

if getattr(context, 'getPortalType', None) is not None:
  if hasDuplicateActions(context.getPortalType(), user_name):
    return filterDuplicateActions(actions)
return actions
