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
  # kw can contain limit, sort_on and similar runtime information
  object_list = [x.getObject() for x in context.portal_catalog(uid=uid, **kw)]
  # only docs WITHOUT relations can be deleted
  return [x for x in object_list if  x.getRelationCountForDeletion() == 0]
