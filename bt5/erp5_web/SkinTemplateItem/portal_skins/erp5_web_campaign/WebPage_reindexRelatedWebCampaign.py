from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery

reference=context.getReference()
if not reference:
  return

for web_campaign in context.portal_catalog(
  portal_type='Web Campaign',
  validation_state='published',
  query= ComplexQuery(
    SimpleQuery(aggregate_reference=reference),
    SimpleQuery(causality_reference=reference),
    logical_operator='OR')
):
  web_campaign.activate(after_method_id=('immediateReindexObject')).reindexObject()
