portal = context.getPortalObject()

project = None
if project_id:
  project = portal.project_module[project_id]

result = context.SupportRequest_getSupportTypeListFromProjectValue(project)

if json_flag:
  from json import dumps
  container.REQUEST.RESPONSE.setHeader('content-type', 'application/json')
  return dumps(result)

return result
