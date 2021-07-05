from Products.ZSQLCatalog.SQLCatalog import ComplexQuery, SimpleQuery

is_access_tool_enabled = (context.getPortalObject().portal_preferences
                          .getPreferredHtmlStyleAccessTool())

query = ComplexQuery(
  SimpleQuery(id="%\\_module", comparison_operator="like"),
  SimpleQuery(meta_type="ERP5 Folder"),
  logical_operator='AND'
)

if is_access_tool_enabled:
  query = ComplexQuery(
    query,
    SimpleQuery(id="portal\\_%", comparison_operator="like"),
    logical_operator='OR')

return ComplexQuery(
  query,
  SimpleQuery(parent_uid=0),
  SimpleQuery(id=value, comparison_operator="like" if "%" in value else "="),
  logical_operator='AND')
