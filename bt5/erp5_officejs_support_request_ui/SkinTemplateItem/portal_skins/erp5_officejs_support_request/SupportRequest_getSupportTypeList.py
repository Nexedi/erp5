portal = context.getPortalObject()

if project_id:
  project_list = portal.portal_catalog(portal_type="Project", id=project_id, limit=1)
else:
  project_list = portal.portal_catalog(portal_type="Project", validation_state="validated", limit=1)

try:
  project = project_list[0]
except IndexError:
  project = None

result = context.SupportRequest_getSupportTypeListFromProjectValue(project)

if json_flag:
  from json import dumps
  return dumps(result)

return result
