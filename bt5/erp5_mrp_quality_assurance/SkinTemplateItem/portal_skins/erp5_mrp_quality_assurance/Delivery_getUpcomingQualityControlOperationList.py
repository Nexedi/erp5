search_dict = {
  "portal_type": ("Quality Control", "Traceability", "Gate", "SMON", "ACOM"),
  "sort_on" : (('int_index', 'ascending'),),
  "validation_state": 'expected',
  "strict_publication_section_uid": context.portal_categories.publication_section.quality_insurance.getUid(),
  "strict_causality_uid": context.getUid()
}

return [x for x in context.portal_catalog(**search_dict) if x.getValidationState() == 'expected']
