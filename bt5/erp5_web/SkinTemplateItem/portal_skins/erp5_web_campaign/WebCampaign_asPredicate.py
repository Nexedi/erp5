default_page_reference = context.getAggregateReference()
if not default_page_reference:
  return

if context.getValidationState() == 'published':
  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()):
    # Render On Specific Page has higher priority
    causality_reference_list = context.getCausalityReferenceList()
    if causality_reference_list:
      causality_reference_list = [x for x in causality_reference_list if x]
      if not causality_reference_list:
        return None

      new_context  = context.asContext(categories=('display_domain/web_content',))
      return new_context.generatePredicate(membership_criterion_base_category_list = ('display_domain',),
                                           criterion_property_list = ('start_date',))

    else:
      if context.getPublicationSection() and context.getFollowUp() and context.getDisplayDomainList():
        return context.generatePredicate(membership_criterion_base_category_list = ('publication_section', 'follow_up', 'display_domain'),
                                         criterion_property_list = ('start_date',))
return None
