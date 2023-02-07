valide_document_state=('published', 'published_alive')


default_page_reference = context.getAggregateReference()
if not default_page_reference:
  return

if context.getValidationState() == 'published':
  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()):
    default_page = context.portal_catalog.getResultValue(
      portal_type='Web Page',
      validation_state=valide_document_state,
      reference=default_page_reference
    )
    if not default_page:
      return None
    # Render On Specific Page has higher priority
    causality_reference_list = context.getCausalityReferenceList()
    if causality_reference_list:
      causality_reference_list = [x for x in causality_reference_list if x]
      if not causality_reference_list:
        return None
      specific_page_list = context.portal_catalog(
        portal_type='Web Page',
        validation_state=valide_document_state,
        reference=causality_reference_list)

      if specific_page_list:
        new_category_list = ['display_domain/web_content']
        for specific_page in specific_page_list:
          new_category_list = new_category_list + specific_page.getFollowUpList(base=True) + specific_page.getPublicationSectionList(base=True)

        new_context  = context.asContext(categories=set(new_category_list))
        return new_context.generatePredicate(membership_criterion_base_category_list = ('publication_section', 'follow_up', 'display_domain'),
                                         criterion_property_list = ('start_date',))

    else:
      if context.getPublicationSection() and context.getFollowUp() and context.getDisplayDomainList():
        return context.generatePredicate(membership_criterion_base_category_list = ('publication_section', 'follow_up', 'display_domain'),
                                         criterion_property_list = ('start_date',))
return None
