# this script has a parameter named `id`
# pylint: disable=redefined-builtin
"""Delete an action on a type informations from types tool.
"""
assert context.meta_type in ('ERP5 Type Information', 'ERP5 Base Type'), context.meta_type

if context.meta_type == 'ERP5 Type Information':
  existing_actions_indexs = []
  for idx, ai in enumerate(context.listActions()):
    if ai.getId() == id:
      existing_actions_indexs.append(idx)

  if existing_actions_indexs:
    context.deleteActions(existing_actions_indexs)
else:
  existing_actions_ids = []
  for action in context.objectValues(spec='ERP5 Action Information'):
    if action.getReference() == id:
      existing_actions_ids.append(action.getId())
  if existing_actions_ids:
    context.manage_delObjects(existing_actions_ids)

return 'Set Successfully.'
