portal = context.getPortalObject()
result = []
sql_result = portal.ERP5Site_zGetDuplicateLoginReferenceList()
if len(sql_result):
  from Products.CMFActivity.ActiveResult import ActiveResult
  from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
  query = ComplexQuery(
    *[ComplexQuery(SimpleQuery(portal_type=i['portal_type']),
                   SimpleQuery(reference=i['reference'])) for i in sql_result],
    operator='OR')
  active_result = ActiveResult()
  for i in portal.portal_catalog(
      select_list=('portal_type', 'reference',),
      query=query):
    result.append('%r, %r, %r' % (i['portal_type'], i['reference'], i['path']))
  active_result.edit(summary='Logins having the same reference exist',
                     severity=len(sql_result),
                     detail='\n'.join(result))
  active_process = context.newActiveProcess()
  active_process.postResult(active_result)
  return active_process
