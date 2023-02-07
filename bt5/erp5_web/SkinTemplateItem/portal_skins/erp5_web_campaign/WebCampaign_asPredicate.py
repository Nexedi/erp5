default_page_reference = context.getAggregateReference()
if not default_page_reference:
  return

if context.getValidationState() == 'published':
  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()):
    causality_value_list = context.getCausalityValueList()
    if causality_value_list:
      specify_document = []
      for causality_value in causality_value_list:
        if causality_value.getPortalType() == 'Web Page':
          specify_document.append(causality_value.getReference())
        else:
          specify_document.append(causality_value.getRelativeUrl())
      new_context = context.asContext()
      new_context.edit(
        specify_document= specify_document,
        display_domain='specify_document'
      )
      return new_context.generatePredicate(
        membership_criterion_base_category_list = ('display_domain',),
        criterion_property_list = ('start_date', 'specify_document',)
      )

    else:
      # render on web page which match publication and follow up
      if context.getPublicationSection() and context.getFollowUp():
        new_context = context.asContext()
        new_context.edit(
          display_domain='web_content'
        )
        return new_context.generatePredicate(
          membership_criterion_base_category_list = ('publication_section', 'follow_up', 'display_domain', ),
          criterion_property_list = ('start_date',)
        )
return None
