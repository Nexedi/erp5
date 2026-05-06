"""
  Search text query generator. Accepts a string and returns a ComplexQuery.
  For example:

  search_text = DMS reference:bt5-dms version:001 language:bg mine:yes (portal_type:Presentation OR portal_type:File) created:12m contributor_title:%tyagov%

  will parse search_text and generate a complexQuery which will return all documents which:
  - have full_text searchable text containing "DMS"
  - have reference equal to bt5-dms
  - have portal_type "Presentation" OR "File"
  - are created within last 12 months
  - are owned by current logged in user
  - are contributed by given Person's title
  - etc ..
"""
if 'full_text' in context.sql_search_tables:
  column = 'SearchableText'
else:
  column = 'title'
node = context.Base_getAdvancedSearchSyntaxTreeNode(value, column=column)
if node is None:
  return context.buildSingleQuery(column, value)
else:
  return context.buildQueryFromAbstractSyntaxTreeNode(node, column, ignore_unknown_columns=True)
