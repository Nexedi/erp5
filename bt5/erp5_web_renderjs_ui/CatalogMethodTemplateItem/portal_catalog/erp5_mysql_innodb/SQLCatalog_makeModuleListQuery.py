portal = context.getPortalObject()
is_access_tool_enabled = (portal.portal_preferences
                          .getPreferredHtmlStyleAccessTool())

sql_catalog = portal.portal_catalog.getSQLCatalog()
query = sql_catalog.buildQuery({
  "id": "%\\_module",
  "meta_type": "ERP5 Folder"
})

if is_access_tool_enabled:
  query = sql_catalog.buildQuery({
    "id": "portal\\_%",
    "query": query
  }, operator="or")

return sql_catalog.buildQuery({
  "id": value,
  "parent_uid": 0,
  "query": query
})
