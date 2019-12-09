from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
kw.pop('relative_url', None)
kw.pop('follow_up_uid', None)
portal_catalog=context.getPortalObject().portal_catalog
project_object_list = portal_catalog(
           portal_type=portal_type,
           source_project_title=context.getTitle(), **kw)
kw['query'] = Query(relative_url='%s/%%' % context.getRelativeUrl().replace('_', r'\_'))
if project_object_list:
  kw['query'] = ComplexQuery(
    kw['query'],
    Query(uid=[x.getUid() for x in project_object_list]),
    logical_operator='or')
return portal_catalog(portal_type=portal_type, limit=limit, **kw)
