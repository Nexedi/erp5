# XXX strict membership is missing ?
# ideally strict membership should be an option for each category, but this API
# does not exist in predicates.

# TODO: support virtual "All other nodes"


return context.generatePredicate(
      multimembership_criterion_base_category_list = ('resource',),
      criterion_property_list = ('start_date', 'stop_date'))
