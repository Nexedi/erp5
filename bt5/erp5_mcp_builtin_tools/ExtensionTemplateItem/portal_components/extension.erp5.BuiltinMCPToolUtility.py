"""Utility functions for ERP5 MCP server"""

def PortalType_getViewActionText(portal_type):
  """Retrieve the raw TALES expression text for the 'view' action of a portal type."""
  for action_information in portal_type.getActionInformationList():
    if action_information.getReference() == "view":
      action_text = action_information.getAction().text
      return action_text


def PortalType_getListMethod(context, portal_type_id, module_portal_type_id_list):
  for module_portal_type_id in module_portal_type_id_list:
    listbox = context.PortalType_getListBox(portal_type_id, [module_portal_type_id])
    if listbox:
      mod = context.getPortalObject().portal_catalog(portal_type=module_portal_type_id)[0].getObject()
      break
  list_method = listbox.get_value("list_method")
  if list_method:
    list_method_name = list_method.method_name
  else:
    list_method_name = "searchFolder"
  assert isinstance(list_method_name, str), "bad list_method_name: %s (of listbox %s)" % (list_method_name, listbox)
  return getattr(mod, list_method_name)

