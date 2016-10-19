uid_list = [context.getUid()]
def iterate(container):
  for project_line in container.objectValues(portal_type='Project Line'):
    uid_list.append(project_line.getUid())
    iterate(project_line)

iterate(context)

if 'source_project_uid' in kw:
  del kw['source_project_uid']

return context.portal_catalog(source_project_uid=uid_list, **kw)
