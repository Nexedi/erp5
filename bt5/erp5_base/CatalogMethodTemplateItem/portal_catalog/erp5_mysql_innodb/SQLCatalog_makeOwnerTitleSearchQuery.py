from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
return SimpleQuery(owner=[
  x.user_id for x in
  context.getPortalObject().portal_catalog(
    select_list=['user_id'],
    title=value,
  )
] or value or -1)
