portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
# PR(B) = (1-d) + d x ( PR(A1) / N(A1) + ... + PR(An) / N(An) )
d = 0.85
decimal_length = 10
multiplier = pow(10, decimal_length)

rank = 0

# Search all document linking to the context
for sql_result in portal_catalog(
  select_list=['search_rank'],
  **{'category.category_uid': context.getUid()}
):
  rank += (float(sql_result.search_rank)) / len(sql_result.getCategoryList())

return int(((1 - d) + d * rank) * multiplier)
