request = container.REQUEST
project_title = ''
try:
  return request.other[context.project_uid]
except KeyError:
  if context.project_uid:
    project = context.getPortalObject().portal_catalog.getobject(context.project_uid)
    if project is not None:
      project_title = project.getTitle()
  
request.other[context.project_uid] = project_title
return project_title
