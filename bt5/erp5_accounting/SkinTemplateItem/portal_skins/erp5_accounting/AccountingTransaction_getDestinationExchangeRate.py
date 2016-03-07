return context.getResourceValue().getPrice(
    context=context.asContext(categories=[context.getResource(base=True),
                                          context.getDestinationSectionValue().getPriceCurrency(base=True)],
                              start_date=context.getStopDate()))
