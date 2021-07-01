from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery

is_access_tool_enabled = (context.getPortalObject().portal_preferences
                          .getPreferredHtmlStyleAccessTool())

simple_query = SimpleQuery(parent_uid=0)
module_query = ComplexQuery(
  SimpleQuery(id="%\\_module", comparison_operator="like"),
  SimpleQuery(meta_type="ERP5 Folder"),
  logical_operator='AND'
)

if is_access_tool_enabled:
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

return ComplexQuery(
  query,
  SimpleQuery(id=value, comparison_operator="like"),
  logical_operator='AND')
