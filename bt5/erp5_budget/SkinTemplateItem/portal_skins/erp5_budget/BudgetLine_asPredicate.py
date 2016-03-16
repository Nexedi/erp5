context = context.asContext(
             _range_criterion = {'start_date': (context.getStartDateRangeMin(),
                                                context.getStartDateRangeMax())
                               })
return context



return context.generatePredicate(criterion_property_list=('start_date', 'stop_date'))

return context.generatePredicate(_range_criterion = {'start_date': (context.getStartDate(),
                                               context.getStopDate())
                               })

return context.generatePredicate(criterion_property_list=('start_date',))

return context.generatePredicate(multimembership_criterion_base_category_list = ('resource',),
                                                      criterion_property_list = ('start_date',))




context = context.asContext(
             criterion_property_list=['start_date'], 
             range_criterion = {'start_date': (context.getStartDate(),
                                               context.getStopDate())
                               })
return context
