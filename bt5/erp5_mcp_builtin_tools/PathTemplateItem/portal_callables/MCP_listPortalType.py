from Products.ERP5Type.Utils import str2unicode, unicode2str

page_size = 100
portal = context.getPortalObject()
skins, callables = portal.portal_skins, portal.portal_callables
renderTextTable = callables['MCPUtility_renderTextTable']
Listbox_getBrainValue = skins.erp5_hal_json_style.Listbox_getBrainValue

page = int(page)  # XXX: why do we need to cast this?

contained_portal_type_mapping_dict = context.Base_getContainedPortalTypeMappingDict()
try:
  module_portal_type_id = contained_portal_type_mapping_dict[portal_type_id]
except KeyError:
  err_msg = "Use MCP_listPortalTypes to find all supported/known portal types."
  raise ValueError("Portal type '%s' is not contained in any module! %s" % (portal_type_id, err_msg))
column_map = context.PortalType_getColumnMap(portal_type_id, [module_portal_type_id])
column_title_to_name = {c["title"]: c["name"] for c in column_map.values()}

if not column_list:
  column_list = [c["title"] for c in column_map.values() if c["default"]]

def getColumnName(column_title_or_name):
  try:
    return column_title_to_name[column_title_or_name]
  except KeyError:
    bad_column_msg = "Unknown column '%s'. Use MCP_getPortalTypeSchema to find all columns of '%s'" % (
      column_title_or_name, portal_type_id)
    assert column_title_or_name in column_map, bad_column_msg
    return column_title_or_name

# User given column list contains either the title or the name of a column.
# If it's a title, then we need to convert it to a column name.
# Furthermore, we need to drop duplicates.
column_name_list, safe_column_list = [], []
for column_title_or_name in column_list:
  column_name = getColumnName(column_title_or_name)
  if column_name not in column_name_list:
    column_name_list.append(column_name)
    safe_column_list.append(column_title_or_name)
column_list = safe_column_list

# Define search filter
kwargs = {}
for k, v in filters.items():
  if v is not None:
    column_name = getColumnName(k)
    assert column_map[column_name]["filterable"], "Cannot use column '%s' in 'filters' argument, because the column is not filterable!" % k
    if isinstance(v, unicode):
        kwargs[column_name] = v.encode('utf-8')
    else:
        kwargs[column_name] = str(v)

# Define sort filter
ALLOWED_DIRECTION_TUPLE = ("ascending", "descending")
sort_on_safe = []
for pair in sort_on:
  assert isinstance(pair, list), "Found bad value '%s' in sort_on parameter: each entry must be a list with two elements [COLUMN_NAME, DIRECTION]" % pair
  column_name = getColumnName(pair[0])
  assert column_map[column_name]["filterable"], "Cannot use column '%s' in 'sort_on' argument, because the column is not filterable!" % pair[0]
  direction = pair[1]
  assert direction in ALLOWED_DIRECTION_TUPLE, "Bad direction '%s' in sort_on parameter. Supported directions are %s" % (direction, ALLOWED_DIRECTION_TUPLE)
  sort_on_safe.append((column_name, direction))
sort_on_safe = tuple(sort_on_safe)

list_method = context.PortalType_getListMethod(
  context, portal_type_id, [module_portal_type_id]
)

# XXX That's not good:
#  1. We have to send two queries
#  2. We don't limits here- what's about massive tables?
#      - or does it auto-limit? In this case, count isn't reliable
# NOTE We cannot use query count because this raises an error if there are
#   unknown columns (even if ignore_unknown_columns is set). It also wouldn't
#   be correct to use it, because the custom 'list_method' may auto-map columns
#   to other columns e.g. may apply a different query than if we send the same
#   parameter straight to a count query).
count = len(list_method(portal_type=portal_type_id, sort_on=sort_on_safe, limit=None, **kwargs))

start = page * page_size
end = min(start + page_size, count)

listbox = context.PortalType_getListBox(portal_type_id, [module_portal_type_id])


# adaption of 'ListBoxRenderer.getEditableField'
def getEditableFieldForColumn(column_name):
  alias = column_name.replace('.', '_')
  form = listbox.aq_parent
  field = listbox
  original_field_id = field.id
  while True:
    for field_id in {original_field_id, field.id}:
      field_name = "%s_%s" % (field_id, alias)
      if form.has_field(field_name, include_disabled=1):
        return form.get_field(field_name, include_disabled=1)
    if field.meta_type != 'ProxyField':
      return None
    field = field.getTemplateField().aq_inner


row_list = []
brains = list_method(
  portal_type=portal_type_id,
  sort_on=sort_on_safe,
  limit=[start, end],
  **kwargs
)
for brain in brains:
  doc = brain.getObject()
  row = {}
  for column_title, column_name in zip(column_list, column_name_list):
    editable_field = getEditableFieldForColumn(column_name)
    v = Listbox_getBrainValue(
      brain,
      doc,
      column_name,
      can_check_local_property=True,
      editable_field=editable_field,
    ) or ""
    v = str2unicode(str(v), errors='replace').strip()
    assert column_title not in row
    row[column_title] = v
  row_list.append(row)

data = dict(portal_type=portal_type_id, count=count, start=start, end=end, rows=row_list)
return renderTextTable(portal_type_id, column_list, row_list, start, end, count), data
