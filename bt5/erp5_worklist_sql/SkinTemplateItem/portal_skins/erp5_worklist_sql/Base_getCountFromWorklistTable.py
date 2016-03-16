# Wrapper for Base_zGetCountFromWorklistTable

where_expression = context.getPortalObject().portal_catalog.buildSQLQuery(query=query, query_table=None)['where_expression']

return context.Base_zGetCountFromWorklistTable(
  where_expression=where_expression,
  select_expression=select_expression,
  group_by_expression=group_by_expression,
  **kw)
