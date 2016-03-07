# We will need to create all checks for all checkbooks
# Then all of them should be set as confirmed
transaction = state_change['object']

line_list = transaction.getMovementList()

for line in line_list:
  aggregate_list = line.getAggregateValueList()
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Check':
      aggregate.setStartDate(transaction.getStartDate())
      aggregate.setDestinationPayment(transaction.getDestinationPayment())
      aggregate.confirm()
