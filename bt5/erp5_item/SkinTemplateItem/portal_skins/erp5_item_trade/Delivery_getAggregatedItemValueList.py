# Return the list of items aggregated by this packing list
aggregate_value_list = []
for movement in context.getIndexableChildValueList():
  aggregate_value_list.extend(movement.getAggregateValueList())
return aggregate_value_list
