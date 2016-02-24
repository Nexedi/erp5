currency_exchange_line = context.getParentValue()
currency = currency_exchange_line.getParentValue()

return context.asContext(_range_criterion=dict(start_date=(currency_exchange_line.getStartDate(),
                                                           currency_exchange_line.hasStopDate() and currency_exchange_line.getStopDate() or None)),
                         membership_criterion_base_category=['price_currency', 'resource', 'currency_exchange_type'],
                         membership_criterion_category=['resource/%s' % currency.getRelativeUrl(),
                                                        currency_exchange_line.getPriceCurrency(base=True),
                                                        context.getCurrencyExchangeType(base=True)])
