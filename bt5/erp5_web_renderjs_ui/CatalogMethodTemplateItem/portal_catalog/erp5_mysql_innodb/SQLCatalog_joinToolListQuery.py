from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, Query

is_developer_mode = (context.getPortalObject().portal_preferences
                     .getPreferredHtmlStyleDevelopperMode())

simple_query = Query(parent_uid=0)
module_query = Query(id=value, meta_type="ERP5 Folder")

if is_developer_mode:
  query = ComplexQuery(
    simple_query,
    ComplexQuery(
      module_query,
      Query(id="portal_%"),
      logical_operator='OR'
    ),
    logical_operator='AND')

else:
  query = ComplexQuery(
    simple_query,
    module_query,
    logical_operator='AND')

return query
