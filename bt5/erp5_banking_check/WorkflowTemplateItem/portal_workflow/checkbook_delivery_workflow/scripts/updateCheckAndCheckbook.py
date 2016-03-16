# XXX: this script is not used any more, since checks are already
# generated when checks & checkbooks are received.

# We will need to create all checks for all checkbooks
# Then all of them should be set as confirmed
transaction = state_change['object']

line_list = transaction.getMovementList()

for line in line_list:
  aggregate_list = line.getAggregateValueList()
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Checkbook':
      aggregate.setStartDate(transaction.getStartDate())
      aggregate.confirm()
      for check in aggregate.objectValues(portal_type='Check'):
        check.confirm()
        check.setStartDate(transaction.getStartDate())
    elif aggregate.getPortalType()=='Check':
      aggregate.setStartDate(transaction.getStartDate())
      aggregate.confirm()
