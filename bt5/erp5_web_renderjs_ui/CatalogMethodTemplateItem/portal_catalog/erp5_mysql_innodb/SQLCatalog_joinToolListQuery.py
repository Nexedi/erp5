from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery

is_developer_mode = (context.getPortalObject().portal_preferences
                     .getPreferredHtmlStyleDevelopperMode())

simple_query = SimpleQuery(parent_uid=0)
module_query = ComplexQuery(
  SimpleQuery(id=value, comparison_operator="like"),
  SimpleQuery(meta_type="ERP5 Folder"),
  logical_operator='AND'
)

if is_developer_mode:
  query = ComplexQuery(
    simple_query,
    ComplexQuery(
      module_query,
      SimpleQuery(id="portal\\_%", comparison_operator="like"),
      logical_operator='OR'
    ),
    logical_operator='AND')

else:
  query = ComplexQuery(
    simple_query,
    module_query,
    logical_operator='AND')

return query
