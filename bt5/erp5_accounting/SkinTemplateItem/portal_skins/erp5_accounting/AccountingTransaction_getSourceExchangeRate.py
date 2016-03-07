return context.getResourceValue().getPrice(
    context=context.asContext(categories=[context.getResource(base=True),
                                          context.getSourceSectionValue().getPriceCurrency(base=True)],
                              start_date=context.getStartDate()))
