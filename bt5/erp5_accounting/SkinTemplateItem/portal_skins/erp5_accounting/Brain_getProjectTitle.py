request = container.REQUEST
project_title = ''
try:
  return request.other[context.project_uid]
except KeyError:
  if context.project_uid:
    brain_list = context.getPortalObject().portal_catalog(uid=context.project_uid, limit=2)
    if brain_list:
      brain, = brain_list
      project_title = brain.getObject().getTitle()

request.other[context.project_uid] = project_title
return project_title
