portal = context.getPortalObject()
portal_types = portal.portal_types

for module_id in module_portal_type_id_list:
  module_portal_type = portal_types[module_id]
  view_action_text = context.PortalType_getViewActionText(module_portal_type)
  if view_action_text is None:
    continue

  name = view_action_text.split("/")[-1]
  try:
    view = getattr(context, name)
  except AttributeError:
    continue

  try:
    listbox = getattr(view, 'listbox')
  except AttributeError:
    continue
  else:
    return listbox
