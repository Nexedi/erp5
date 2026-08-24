from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery
kw.pop('relative_url', None)
kw.pop('follow_up_uid', None)
# documents held by the project, or documents whose source_project is the project
kw['query'] = ComplexQuery(
  Query(relative_url='%s/%%' % context.getRelativeUrl().replace('_', r'\_')),
  Query(source_project_uid=context.getUid()),
  logical_operator='or')
return context.getPortalObject().portal_catalog(
  portal_type=portal_type, limit=limit, **kw)
