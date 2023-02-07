base_category_tuple = ()

if context.getValidationState() == 'published':
  if context.getStartDateRangeMin() and context.getStartDateRangeMax():

    if context.getPublicationSection():
      base_category_tuple += ('publication_section',)

    if context.getPublicationSection():
      base_category_tuple += ('follow_up',)

    return context.generatePredicate(membership_criterion_base_category_list = base_category_tuple,
                                     criterion_property_list = ('start_date',))

return None
