from builtins import str
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
connection = portal.erp5_sql_connection
sql_catalog = portal_catalog.getSQLCatalog(sql_catalog_id)
LIMIT = 100

missing_uid_list = []
i = 0
while True:
  full_text_list = portal_catalog(SearchableText='!=NULL', limit=(i*LIMIT, LIMIT))
  i += 1
  len1 = len(full_text_list)
  if len1 == 0:
    break
  uid_list1 = [str(x.uid) for x in full_text_list]
  result = connection.manage_test('select uid from sphinxse_index where '
                                  'sphinxse_query=\'filter=uid,%s;limit=%s\'' % (','.join(uid_list1), LIMIT))
  if len(result) == len1:
    continue
  uid_list2 = [str(x[0]) for x in result]
  missing_uid_list += [x for x in uid_list1 if x not in uid_list2]
if missing_uid_list:
  return [(x.uid, x.path) for x in portal_catalog(uid=missing_uid_list)]
