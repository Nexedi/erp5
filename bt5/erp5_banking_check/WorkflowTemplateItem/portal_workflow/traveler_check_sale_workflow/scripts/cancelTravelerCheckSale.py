# Make sure that the states comes back to
# draft for all checks
transaction = state_change['object']

line_list = transaction.getMovementList()

for line in line_list:
  aggregate_list = line.getAggregateValueList()
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Check':
      aggregate.unconfirm()
