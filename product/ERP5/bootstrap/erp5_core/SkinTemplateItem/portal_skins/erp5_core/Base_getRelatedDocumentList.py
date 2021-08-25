from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
kw.pop('relative_url', None)
kw.pop('follow_up_uid', None)

portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

if portal_type is None:
  portal_type = portal.getPortalDocumentTypeList() + portal.getPortalEmbeddedDocumentTypeList()
limit = kw.pop('limit', None)
follow_up_related_document_list = portal_catalog(
  portal_type=portal_type,
  follow_up_uid=context.getUid(),
)
document_query = Query(relative_url='%s/%%' % context.getRelativeUrl().replace('_', r'\_'))
if follow_up_related_document_list:
  document_query = ComplexQuery(
    document_query,
    Query(uid=[x.getUid() for x in follow_up_related_document_list]),
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
  limit=limit,
  **kw)
