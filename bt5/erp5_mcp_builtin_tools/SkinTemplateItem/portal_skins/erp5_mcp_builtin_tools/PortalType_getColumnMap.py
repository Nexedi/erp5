""""""

portal = context.getPortalObject()
portal_types = portal.portal_types

list_method = context.PortalType_getListMethod(
  context, portal_type_id, module_portal_type_id_list
)

def Column(name, title=None, filterable=None, default=None, type_="unknown"):
  if default is None:
    default = title in default_property_list
  if filterable is None:
    # NOTE We cannot just ask sql_catalog if it's a valid column, because this also depends
    # on the specific portal_type
    test_query = "t"
    if "date" in name:
      test_query = "2008 GMT+9"
    try:
      list_method(portal_type=portal_type_id, **{name: test_query})
    except (TypeError, ValueError):
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

listbox = context.PortalType_getListBox(portal_type_id, module_portal_type_id_list)
for column_list_name in ("columns", "all_columns"):
  for name, title in listbox.get_value(column_list_name):
    try:
      column = column_map[name]
    except KeyError:
      column = column_map[name] = Column(name, title, default=True)
    else:
      column["title"] = title
      column["default"] = True

restricted_column_list = context.PortalType_getRestrictedColumnList(portal_type_id)
if restricted_column_list is not None:
  for name in column_map.keys():
    if name not in restricted_column_list:
      del column_map[name]

return column_map
