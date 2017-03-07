from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery

if document_type == 'Image':
  portal_type = ['Image']
else:
  portal_type = [x for x in context.getPortalDocumentTypeList() if x != 'Image']

return ComplexQuery(
  Query(portal_type=portal_type),
  ComplexQuery(
    Query(validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'),
          reference='!=None'),
    Query(validation_state='embedded', parent_uid=context.getUid()),
    logical_operator='or'),
  logical_operator='and')
