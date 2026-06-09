from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
owner = [
  x.user_id for x in
  context.getPortalObject().portal_catalog(
    select_list=['user_id'],
    title=value,
  )
] or value
if owner:
  return SimpleQuery(owner=owner)
return SimpleQuery(uid=-1)
