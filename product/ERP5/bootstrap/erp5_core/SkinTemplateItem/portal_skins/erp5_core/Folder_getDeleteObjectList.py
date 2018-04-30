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
  return list(
           filter(lambda x: x.getRelationCountForDeletion() == 0,  # only docs WITHOUT relations can be deleted
                  map(lambda x: x.getObject(),
                      context.portal_catalog(uid=uid, **kw))  # kw can contain limit, sort_on and similar runtime information
           )
         )
