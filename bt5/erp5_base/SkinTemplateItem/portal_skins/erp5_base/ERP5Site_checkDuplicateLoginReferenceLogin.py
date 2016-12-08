from Products.CMFActivity.ActiveResult import ActiveResult
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
portal = context.getPortalObject()
result = []
sql_result = portal.ERP5Site_zGetDuplicateLoginReferenceList()
if len(sql_result):
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
elif context.sense():
  active_result = ActiveResult()
  active_result.edit(summary='Logins having the same reference does not exist',
                     severity=0)
else:
  return

active_process = context.newActiveProcess()
active_process.postResult(active_result)
return active_process
