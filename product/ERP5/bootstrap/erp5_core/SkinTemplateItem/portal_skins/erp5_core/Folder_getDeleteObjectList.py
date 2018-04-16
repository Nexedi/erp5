# XXX This is a hack which allow to delete non indexed Template
# Never call listFolderContents in a place where there could be million of
# documents!

if context.getPortalType() == 'Preference':
  result = []
  for i in context.listFolderContents():
    if i.getUid() in uid:
      result.append(i)
  return result
else:
  # it is enough to search with uids because it is the most specific attribute
  return context.portal_catalog(uid=uid, **kw)
