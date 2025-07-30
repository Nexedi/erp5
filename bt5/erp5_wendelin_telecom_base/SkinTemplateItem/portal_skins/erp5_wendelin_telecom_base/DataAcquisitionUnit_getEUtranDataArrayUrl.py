for line in context.getAggregateRelatedValueList(portal_type='Data Analysis Line'):
  if line.getVariationTitle() == 'e_utran':
    data_array = line.getAggregate(portal_type='Data Array')
    if data_array:
      return data_array
