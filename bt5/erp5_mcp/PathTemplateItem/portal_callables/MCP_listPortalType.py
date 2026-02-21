# TODO: Optimize column handling for better performance
#
# Current implementation retrieves all requested columns by fetching the full
# document (brain.getDocument()) and accessing properties, which is very slow
# as it loads each document from the ZODB.
#
# To optimize:
#
# 1. Differentiate between "real" columns (stored in SQL and available directly
#    on brain objects) and "virtual" columns.
#
# 2. For real columns:
#    - Add them to the 'select_list' parameter of the catalog query
#    - Access values directly from brain objects (brain.column_name)
#    - This avoids loading the full document entirely
#
# 3. For virtual columns:
#    - Must still use brain.getDocument() to access them
#
# 4. Implementation approach:
#    - Use portal_catalog.getSQLCatalog().getColumnMap() to identify real columns
#    - Note: getColumnMap() is a protected method, and would therefore need an
#      external method
#    - For real columns, read from brain; for virtual, fall back to document
#    - 'virtual' could be added as property in 'PortalType_getColumnMap'
#    - Then there are 3 types of properties:
#      - real column     (filterable=True)
#      - virtual column  (filterable=True)
#      - normal property (filterable=False)

from Products.ERP5Type.Utils import str2unicode, unicode2str

page_size = 100
portal = context.getPortalObject()
catalog = portal.portal_catalog
callables = portal.portal_callables
getAnyProperty = callables['MCPUtility_getAnyProperty']
renderTextTable = callables['MCPUtility_renderTextTable']

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

count = catalog.countResults(portal_type=portal_type_id, **kwargs)[0][0]
start = page * page_size
end = min((page + 1) * page_size, count)

row_list = []
brains = catalog(
  portal_type=portal_type_id,
  sort_on=sort_on_safe,
  limit=[start, end],
  **kwargs
)
for brain in brains:
  doc = brain.getObject()
  row = {}
  for column_title, column_name in zip(column_list, column_name_list):
    v = getAnyProperty(doc, column_name)
    v = str2unicode(str(v), errors='replace').strip()
    row[column_title] = v
  row_list.append(row)

data = dict(portal_type=portal_type_id, count=count, start=start, end=end, rows=row_list)
return renderTextTable(portal_type_id, column_list, row_list, start, end, count), data
