# Make sure to put back checks in the confirm state
transaction = state_change['object']

line_list = transaction.getMovementList()

for line in line_list:
  aggregate_list = line.getAggregateValueList()
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Check':
      # Make sure it is not possible to take this
      # check again
      aggregate.unarchive()
