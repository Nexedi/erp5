if context.getValidationState() == 'published' and context.getAggregateReference():
  return context.generatePredicate(criterion_property_list = ('start_date',))

return None
