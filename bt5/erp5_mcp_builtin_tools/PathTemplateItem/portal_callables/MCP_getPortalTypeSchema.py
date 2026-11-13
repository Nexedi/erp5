from Products.ERP5Type.Utils import unicode2str

portal = context.getPortalObject()

err_msg = "Use MCP_listPortalTypes to find all supported/known portal types."
assert portal_type_id in portal.portal_types, "Cannot find portal type '%s': %s" % (portal_type_id, err_msg)

contained_portal_type_mapping_dict = context.Base_getContainedPortalTypeMappingDict()
try:
  module_portal_type_id = contained_portal_type_mapping_dict[portal_type_id]
except KeyError:
  raise ValueError("Portal type '%s' is not contained in any module! %s" % (portal_type_id, err_msg))
column_map = context.PortalType_getColumnMap(portal_type_id, [module_portal_type_id])

column_dict = {}
for column in column_map.values():
  column_dict[column["title"]] = {k: v for k, v in column.items() if k not in ("title", "name")}

schema = {"portal_type": portal_type_id, "columns": column_dict}

# Build human-readable display
lines = []
lines.append("COLUMN SCHEMA FOR: %s" % portal_type_id)
lines.append("=" * len(lines[0]))
lines.append("")
lines.append("Available columns (%s total):" % len(column_dict))
lines.append("")

for title, props in sorted(column_dict.items()):
  lines.append("  %s" % title)
  if props:
    prop_lines = []
    for key, value in sorted(props.items()):
      prop_lines.append("%s: %s" % (key, value))
    lines.append("    (%s)" % ", ".join(prop_lines))

text = unicode2str("\n".join(lines))

return text, schema
