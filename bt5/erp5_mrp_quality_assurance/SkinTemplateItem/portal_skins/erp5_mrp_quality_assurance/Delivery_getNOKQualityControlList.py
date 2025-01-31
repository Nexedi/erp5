kw['quality_assurance_relative_url'] = 'quality_assurance/result/nok'
kw['portal_type'] = 'Quality Control'
kw['validation_state'] = 'posted'
kw['strict_causality_uid'] = context.getUid()
kw["strict_publication_section_uid"] = context.portal_categories.publication_section.quality_insurance.getUid()


return [x for x in context.portal_catalog(**kw) if x.getValidationState() == 'posted']
