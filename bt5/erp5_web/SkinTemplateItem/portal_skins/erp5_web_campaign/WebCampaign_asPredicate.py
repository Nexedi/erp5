if context.getValidationState() == 'published':
  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()) and context.getPublicationSection() and context.getFollowUp():
    return context.generatePredicate(membership_criterion_base_category_list = ('publication_section', 'follow_up'),
                                     criterion_property_list = ('start_date',))

return None
