from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
query = ComplexQuery(
  SimpleQuery(portal_type=portal_type),
  SimpleQuery(reference=reference),
)
login_list = [x for x in context.getPortalObject().portal_catalog(
  select_list=('reference',),
  query=query)
  if x.reference == reference]
if ignore_uid is not None:
  login_list = [x for x in login_list if x.uid != ignore_uid]
return len(login_list) > 0
