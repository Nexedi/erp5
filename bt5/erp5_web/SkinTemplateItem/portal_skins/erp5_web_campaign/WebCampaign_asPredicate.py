default_page_reference = context.getAggregateReference()
if not default_page_reference:
  return

if context.getValidationState() == 'published':
  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()):
    # Render On Specify Page has higher priority
    if context.getDisplayDomainList() == ['specify_page']:
      causality_reference_list = [x for x in context.getCausalityReferenceList() if x]
      if not causality_reference_list:
        return None
      return context.generatePredicate(membership_criterion_base_category_list = ('display_domain',),
                                       criterion_property_list = ('start_date',))

    else:
      if context.getPublicationSection() and context.getFollowUp() and context.getDisplayDomain():
        return context.generatePredicate(membership_criterion_base_category_list = ('publication_section', 'follow_up', 'display_domain'),
                                         criterion_property_list = ('start_date',))
return None
