from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, Query, ComplexQuery


ME = context.getCausalityValue(portal_type='Manufacturing Execution')

if not ME:
  return []

portal = context.getPortalObject()
search_dict = {
  "sort_on" : (('int_index', 'ascending'),),
  "strict_publication_section_uid": portal.portal_categories.publication_section.quality_insurance.getUid(),
  "query":  ComplexQuery(
    ComplexQuery(
      SimpleQuery(portal_type=("Quality Control", "Traceability", "Gate", "SMON", "ACOM")),
      SimpleQuery(validation_state='expected'),
      logical_operator='AND'),
    ComplexQuery(
      SimpleQuery(portal_type='Quality Control'),
      SimpleQuery(validation_state='posted'),
      SimpleQuery(quality_assurance_relative_url='quality_assurance/result/nok'),
      logical_operator='AND'),
     logical_operator='OR'),
  "strict_causality_uid": ME.getUid(),
  "int_index": Query(int_index=context.getIntIndex(), range='<')
}

return portal.portal_catalog(**search_dict)
