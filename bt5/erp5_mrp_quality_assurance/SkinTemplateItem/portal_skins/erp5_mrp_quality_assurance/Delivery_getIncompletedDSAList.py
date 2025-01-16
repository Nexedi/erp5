from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery

vin = context.getAggregateValue(portal_type='VIN')
if not vin:
  po = context.getCausalityValue(portal_type='Production Order')
  if po:
    for me in po.getCausalityRelatedValueList(portal_type='Manufacturing Execution'):
      vin = me.getAggregateValue(portal_type='VIN')
      if vin:
        break

if not vin:
  return []

query_list = []

if nok:
  query_list.append(
    ComplexQuery(
      SimpleQuery(portal_type='Quality Control'),
      SimpleQuery(validation_state='posted'),
      SimpleQuery(quality_assurance_relative_url='quality_assurance/result/nok'),
      logical_operator='AND')
  )

if not_started:
  query_list.append(
    ComplexQuery(
      SimpleQuery(portal_type=("Quality Control", "Traceability")),
      SimpleQuery(validation_state=('queued', 'confirmed')),
      logical_operator='AND'),
  )
context.log(context.getRelativeUrl())
search_dict = {
  "sort_on" : (('int_index', 'ascending'),),
  "strict_publication_section_uid": context.portal_categories.publication_section.electronic_insurance.getUid(),
  "query":  ComplexQuery(
    logical_operator='OR',
    *query_list
    ),
  "strict_aggregate_uid": vin.getUid()
}


return context.portal_catalog(**search_dict)
