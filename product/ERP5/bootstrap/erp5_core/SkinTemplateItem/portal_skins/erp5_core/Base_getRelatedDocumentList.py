from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
kw.pop('relative_url', None)
kw.pop('follow_up_uid', None)

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

if portal_type is None:
  portal_type = portal.getPortalDocumentTypeList() + portal.getPortalEmbeddedDocumentTypeList()

document_query = ComplexQuery(
  Query(follow_up_uid=context.getUid()),
  Query(relative_url='%s/%%' % context.getRelativeUrl().replace('_', r'\_')),
  logical_operator='or'
)
if query is None:
  query = document_query
else:
  query = ComplexQuery(
    query,
    document_query,
    logical_operator='and'
  )

return portal_catalog(
  portal_type=portal_type,
  query=query,
  **kw)
