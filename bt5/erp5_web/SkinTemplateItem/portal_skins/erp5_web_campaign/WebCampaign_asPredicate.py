default_page_reference = context.getAggregateReference()
if not default_page_reference:
  return

if context.getValidationState() == 'published':
  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()):
    causality_value_list = context.getCausalityValueList()
    if causality_value_list:
      # render on specify web page
      causality_value_list = [x for x in causality_value_list if x.getPortalType() == 'Web Page']
      if causality_value_list:
        specify_document_reference_list = [x.getReference() for x in causality_value_list]
        new_context = context.asContext()
        new_context.edit(
          specify_document_reference= specify_document_reference_list
        )
        return new_context.generatePredicate(
          membership_criterion_base_category_list = ('publication_section', 'follow_up',),
          criterion_property_list = ('start_date', 'specify_document_reference',)
        )

    else:
      # render on web page which match publication and follow up
      if context.getPublicationSection() and context.getFollowUp():
        return context.generatePredicate(
          membership_criterion_base_category_list = ('publication_section', 'follow_up',),
          criterion_property_list = ('start_date',)
        )
return None
