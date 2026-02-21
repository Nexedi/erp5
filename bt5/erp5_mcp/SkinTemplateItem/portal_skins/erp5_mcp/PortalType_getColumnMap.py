""""""

portal = context.getPortalObject()
catalog = portal.portal_catalog
portal_types = portal.portal_types

def Column(name, title=None, filterable=None, default=None, type_="unknown"):
  if default is None:
    default = title in default_property_list
  if filterable is None:
    # NOTE We cannot just ask sql_catalog if it's a valid column, because this also depends
    # on the specific portal_type
    try:
      catalog.buildSQLQuery(portal_type=portal_type_id, sort_on=[(name, 'ascending')])
    except ValueError:
      filterable = False
    else:
      filterable = True

  # TODO Add 'virtual' property to know if column could be retrieved directly through
  # 'select_list' and the brain object.
  return {
    "name": name,
    "title": title or name,
    "filterable": filterable,
    "default": default,
  }


portal_type = portal_types[portal_type_id]
default_property_list = portal_type.getSearchableTextPropertyIdList()

# NOTE This is commented, because for now we only allow listing properties/fields
#   that are explicitly made visible to the user through listbox view definitions
#   of the module.
#
# property_set = portal_type.getInstancePropertySet()
# column_map = {p: Column(p) for p in property_set}
column_map = {"uid": Column("uid", default=True)}


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

  for column_list_name in ("columns", "all_columns"):
    for name, title in listbox.get_value(column_list_name):
      try:
        column = column_map[name]
      except KeyError:
        column = column_map[name] = Column(name, title, default=True)
      else:
        column["title"] = title
        column["default"] = True

  break

restricted_column_list = context.PortalType_getRestrictedColumnList(portal_type_id)
if restricted_column_list is not None:
  for name in column_map.keys():
    if name not in restricted_column_list:
      del column_map[name]

return column_map
