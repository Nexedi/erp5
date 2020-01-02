from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
kw.pop('relative_url', None)
kw.pop('follow_up_uid', None)
portal_catalog=context.getPortalObject().portal_catalog
follow_up_related_document_list = portal_catalog(
           portal_type=portal_type,
           follow_up_uid=context.getUid(), **kw)
kw['query'] = Query(relative_url='%s/%%' % context.getRelativeUrl().replace('_', r'\_'))
if follow_up_related_document_list:
  kw['query'] = ComplexQuery(
    kw['query'],
    Query(uid=[x.getUid() for x in follow_up_related_document_list]),
    logical_operator='or')
return [x.getRelativeUrl() for x in portal_catalog(portal_type=portal_type, limit=limit, **kw)]
