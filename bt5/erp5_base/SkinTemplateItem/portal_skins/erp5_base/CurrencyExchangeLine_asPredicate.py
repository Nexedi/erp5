start_date = context.getStartDate()
stop_date = context.hasStopDate() and context.getStopDate() or None
identity_criterion = {'start_date':(start_date,stop_date)}
return context.asContext(_range_criterion=identity_criterion,
                         membership_criterion_base_category=['price_currency','resource'],
                         membership_criterion_category=['resource/%s' % context.getParentValue().getRelativeUrl(),
                                                        'price_currency/%s' % context.getPriceCurrency()])
