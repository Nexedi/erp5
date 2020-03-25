if context.getSimulationState() in ('started', 'stop', 'delivered') \
    and context.getAggregate(portal_type='Letter Post') is not None:
  # Get the latest Letter Post, in case the Letter was sent
  # more than once. We can load objects into memory, as this case must be
  # extremeley rare
  return sorted(
    context.getAggregateValueList(portal_type='Letter Post'),
    key=lambda x:x.getCreationDate()
  )[-1].absolute_url() + "/getData"
return context.getTextContent()
