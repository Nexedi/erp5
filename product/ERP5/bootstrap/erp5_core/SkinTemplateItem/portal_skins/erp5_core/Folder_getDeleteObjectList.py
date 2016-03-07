# XXX This is a hack which allow to delete non indexed Template
# Never call listFolderContents in a place where there could be million of
# documents!
if context.getPortalType() == 'Preference':
  result = []
  uid_list = kw.get('uid', [])
  for i in context.listFolderContents():
    if i.getUid() in uid_list:
      result.append(i)
  return result
else:
  return context.portal_catalog(**kw)
