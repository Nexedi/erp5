from zExceptions import Unauthorized

portal = context.getPortalObject()
portal_types = context.getPortalObject().portal_types
portal_type_module_mapping = context.Base_getContainedPortalTypeMappingDict(
  ignore_module_exclusion=True
)

portal_type_display_list = []  # human readable
portal_type_data_list = []  # machine readable

excluded_module_portal_type_list = []
for module_id in context.Base_getMCPExcludedModuleList():
  try:
    module = portal[module_id]
  except (KeyError, Unauthorized):
    continue
  excluded_module_portal_type_list.append(module.getPortalType())

for portal_type_id, module_portal_type_id in portal_type_module_mapping.items():
  try:
    portal_type = portal_types[portal_type_id]
  except Unauthorized:
    continue

  try:
    module = portal_types.getDefaultModule(portal_type_id)
  except Unauthorized:
    continue
  try:
    business_application = module.getBusinessApplicationTitle() or ''
  except AttributeError:
    business_application = ""

  description = ""

  if module_portal_type_id in excluded_module_portal_type_list:
    allowed = False
    description = "Querying this Portal Type is not allowed.\n\n"
  else:
    allowed = True

  if context.PortalType_getRestrictedColumnList(portal_type_id) is not None:
    description = "This Portal Type is restricted.\n\n"
    restricted = True
  else:
    restricted = False

  description += "\n".join([line.strip() for line in portal_type.getDescription().splitlines()])

  display = "%s\n%s\n%s\n" % (portal_type_id, "-" * len(portal_type_id), description)
  portal_type_display_list.append(display)

  data = {
    "id": portal_type_id,
    "allowed": allowed,
    "restricted": restricted,
    "business_application": business_application,
    "description": description
  }
  portal_type_data_list.append(data)

header = "AVAILABLE PORTAL TYPES (%s total)" % len(portal_type_module_mapping)
text = "%s\n%s\n\n\n%s" % (
  header, "=" * len(header), "\n\n".join(portal_type_display_list)
)

return text, {"portalTypes": portal_type_data_list}
