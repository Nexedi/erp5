portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
# PR(B) = (1-d) + d x ( PR(A1) / N(A1) + ... + PR(An) / N(An) )

if context.getRelativeUrl().startswith('portal_'):
  # Show module content before tools content (Category)
  d = 0.80
else:
  d = 0.85

decimal_length = 10
multiplier = pow(10, decimal_length - 5)

rank = 0

# Search all document linking to the context
for sql_result in portal_catalog(
  select_list=['search_rank'],
  **{'category.category_uid': context.getUid()}
):
  # In case of acquired category, it is not explicitely defined on the document
  category_list_length = len(sql_result.getObject().getCategoryList()) or 1

  rank += (float(sql_result.search_rank) / multiplier) / category_list_length

return int(((1 - d) + d * rank) * multiplier)
