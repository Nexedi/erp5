if context.getValidationState() in ('invalidated', 'deleted'):
  # return a predicate that will never apply
  return context.generatePredicate(criterion_property_list=('uid',))

category_list = [
  'source', 'source_section', 'source_project',
  'destination', 'destination_section', 'destination_project'
]
criterion_list = []

for category in category_list:
  if context.getPropertyList(category):
    criterion_list.append(category)

date_context=context.asContext(
  start_date_range_min=context.getEffectiveDate(),
  start_date_range_max=context.getExpirationDate(),
)

return date_context.generatePredicate(multimembership_criterion_base_category_list=criterion_list,
                                                      criterion_property_list=('start_date',))
