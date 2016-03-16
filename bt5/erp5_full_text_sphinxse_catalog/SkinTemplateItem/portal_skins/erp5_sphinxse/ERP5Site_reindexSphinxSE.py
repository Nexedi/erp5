portal_catalog = context.portal_catalog
sql_catalog = portal_catalog.getSQLCatalog(sql_catalog_id)

LIMIT = 100

i = 0
while True:
  full_text_list = portal_catalog(limit=(i*LIMIT, LIMIT))
  if len(full_text_list) == 0:
    break
  sql_catalog.SQLCatalog_deferFullTextIndex(getPath=[x.path for x in full_text_list])
  i += 1
return 'SphinxSE index will be updated in background.'
