search_dict = {
  "portal_type": "Traceability",
  "sort_on" : (
    ('int_index', 'ascending'),
    ('title', 'ascending')
  ),
  "validation_state": 'expected',
  "strict_causality_uid": context.getUid()
}

return [x for x in context.portal_catalog(**search_dict) if x.getValidationState() == 'expected']
