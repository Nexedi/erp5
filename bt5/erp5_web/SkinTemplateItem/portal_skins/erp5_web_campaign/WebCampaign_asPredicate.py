if not context.getAggregateReference():
  return

if context.getValidationState() == 'published':
  new_context = context.asContext()

  membership_criterion_base_category_list = []
  if context.getPublicationSection():
    membership_criterion_base_category_list.append('publication_section')
  if context.getFollowUp():
    membership_criterion_base_category_list.append('follow_up')

  criterion_property_list = []
  causality_value_list = context.getCausalityValueList()
  if causality_value_list:
    specify_document = []
    for causality_value in causality_value_list:
      if causality_value.getPortalType() == 'Web Page':
        specify_document.append(causality_value.getReference())
      else:
        specify_document.append(causality_value.getRelativeUrl())

    criterion_property_list.append('specify_document')
    new_context.edit(
        specify_document= specify_document,
      )

  if (not membership_criterion_base_category_list) and (not criterion_property_list):
    return

  if (context.getStartDateRangeMin() or context.getStartDateRangeMax()):
    criterion_property_list.append('start_date')
  return new_context.generatePredicate(
    membership_criterion_base_category_list = membership_criterion_base_category_list,
    criterion_property_list = criterion_property_list
  )
return None
