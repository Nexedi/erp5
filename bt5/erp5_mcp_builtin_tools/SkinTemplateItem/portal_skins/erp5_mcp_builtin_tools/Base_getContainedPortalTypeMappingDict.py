from zExceptions import Unauthorized
if ignore_module_exclusion:
  excluded_module_list=[]
else:
  excluded_module_list = context.Base_getMCPExcludedModuleList()
portal = context.getPortalObject()
module_type_set = set(portal.getPortalModuleTypeList())
content_type_to_module = {}
for module_id in portal.objectIds(spec=('ERP5 Folder',)):
  if module_id in excluded_module_list:
    continue
  try:
    module = portal[module_id]
  except (KeyError, Unauthorized):
    module = None
  if module is None or module.getPortalType() not in module_type_set:
    continue
  module_portal_type = module.getPortalType()
  for ti in module.allowedContentTypes():
    content_type_id = ti.getId()
    if content_type_id not in module_type_set:
      content_type_to_module[content_type_id] = module_portal_type
return content_type_to_module
