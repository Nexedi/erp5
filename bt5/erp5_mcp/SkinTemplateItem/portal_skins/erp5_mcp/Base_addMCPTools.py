"""Demo to generate generic tools"""

portal = context.getPortalObject()
portal_callables = portal.portal_callables

#portal_type.getInstancePropertySet()


def getPortalTypeIdList():
  module_type_set = set(portal.getPortalModuleTypeList())
  content_type_set = set()
  for module_id in portal.objectIds(spec=('ERP5 Folder',)):
    try:
      module = portal[module_id]
    except KeyError:
      module = None
    if module is None or module.getPortalType() not in module_type_set:
      continue
    for ti in module.allowedContentTypes():
      content_type_set.add(ti.getId())
  result = sorted(content_type_set - module_type_set)
  return result


def addListPortalTypeTool(portal_type):
  portal_type_id = portal_type.getId()
  tool_id = "MCP_list%s" % portal_type_id.replace(" ", "")
  default_props = portal_type.getSearchableTextPropertyIdList()
  search_field_str = "{%s}" % ", ".join(['"{0}": {0}_filter'.format(field) for field in default_props])
  default_props.insert(0, "id")
  all_props = portal_type.getInstancePropertySet()
  description = """This tool lists documents of the type '{0}'.

{1}

By default, this tool lists for each '{0}' document these properties:

{2}
""".format(
    portal_type_id,
    portal_type.getDescription(),
    "\n".join(["- %s" % p for p in default_props]),
  )
  if tool_id in portal_callables:
    portal_callables.manage_delObjects([tool_id])
  tool = portal_callables.newContent(
    portal_type="MCP Tool",
    id=tool_id,
    description=description,
    body=LIST_PORTAL_TYPE % (repr(default_props), repr(portal_type_id), search_field_str, repr(list(all_props))),
  )
  tool.newContent(
    portal_type="MCP Tool Line",
    int_index=0,
    reference="page",
    type="int",
    parameter_default="python: 0",
    description="The 'page' argument specifies the page index."
  )
  tool.newContent(
    portal_type="MCP Tool Line",
    int_index=1,
    reference="extra_fields",
    type="list",
    parameter_default="python: []",
    description="Specify in a list additional fields that are displayed. This can be any of %s" % list(all_props)
  )
  for i, search_field in enumerate(default_props[1:]):
    description = "Optionally filter by %s (supports exact values or wildcard patterns such as 'hello%%')" % search_field
    tool.newContent(
      portal_type="MCP Tool Line",
      int_index=i + 2,
      reference="%s_filter" % search_field,
      type="str",
      parameter_default="python: None",
      description=description
    )
  tool.setParameterSignatureFromParameterList()  # XXX need interaction workflow
  return "List %s | %s" % (portal_type_id, tool_id)


LIST_PORTAL_TYPE = """
# XXX why do we need to cast this ? when doing MCP Tool/run, page is read as int, but why ?
page = int(page)

props = %s
portal_type = %s
search_field_dict = %s
all_props = %s

kwargs = {}
for k, v in search_field_dict.items():
  if v is not None:
    kwargs[k] = v

portal = context.getPortalObject()
catalog = portal.portal_catalog

count = catalog.countResults(portal_type=portal_type, **kwargs)[0][0]


MAX_WIDTH = 40
MIN_WIDTH = 3

page_size = 1000
start = page * page_size
end = min((page + 1) * page_size, count)

rows = []
for brain in catalog(
  portal_type=portal_type,
  sort_on=(('uid','ascending'),),
  limit=[start, end],
  **kwargs
):
  doc = brain.getObject()
  row = []
  for p in props:
    # XXX this is perhaps not good, we should use erp5 getter e.g. 'get<PROP>'
    v = doc.getProperty(p, "") or ""
    v = str(v).strip()
    row.append(v)
  rows.append(row)

# Calculate column widths (header + data)
widths = []
for i, p in enumerate(props):
  values = [p] + [r[i] for r in rows]
  max_len = max(len(v) for v in values)
  max_len = max(max_len, MIN_WIDTH)
  max_len = min(max_len, MAX_WIDTH)
  widths.append(max_len)

def format_row(r):
  out = []
  for width, cell in zip(widths, r):
    diff = len(cell) - width
    if diff > 0:
      cell = cell[:width-3] + "..."
    elif diff < 0:
      cell = cell + (" " * abs(diff))
    out.append(cell)
  return " | ".join(out)

pretext = "   {}, {} - {} (total count: {})".format(portal_type, start, end, count)
header = format_row(props)
lines = [pretext, "=" * len(pretext), "\\n", header, "=" * len(header)]
for row in rows:
  lines.append(format_row(row))

return "\\n".join(lines)
"""


portal_type_id_list = getPortalTypeIdList()
portal_type_list = [portal.portal_types[p] for p in portal_type_id_list]
for portal_type in portal_type_list:
  print addListPortalTypeTool(portal_type)

return printed
