from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery

causality_uid_list = [context.getUid()]
if context.getPortalType() == 'Manufacturing Execution':
  ipl = context.getOrderRelatedValue(portal_type='Internal Packing List')
  if ipl:
    causality_uid_list.append(ipl.getUid())

pasted_quality_history = context.portal_catalog(
  validation_state='posted',
  strict_publication_section_uid = context.portal_categories.publication_section.quality_insurance.getUid(),
  query = ComplexQuery(
    ComplexQuery(
      SimpleQuery(quality_assurance_relative_url='quality_assurance/result/ok'),
      SimpleQuery(portal_type='Quality Control'),
      logical_operator='AND'),
    SimpleQuery(portal_type=('Gate', 'Traceability', 'Defect Declaration', 'Defect Correction', 'SMON', 'ACOM')),
    logical_operator='OR'),
  strict_causality_uid = causality_uid_list,
  **kw
)
return pasted_quality_history
