from Products.ZSQLCatalog.SQLCatalog import OrQuery, Query
is_developer_mode = (context.getPortalObject().portal_preferences
                     .getPreferredHtmlStyleDevelopperMode())

if is_developer_mode:
  query = Query(id=value)
  return OrQuery(query)
