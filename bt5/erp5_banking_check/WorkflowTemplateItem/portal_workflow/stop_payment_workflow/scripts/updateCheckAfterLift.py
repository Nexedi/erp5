# We will make sure that the check will be usable again
transaction = state_change['object']

line_list = transaction.getMovementList()
portal_workflow = transaction.portal_workflow

for line in line_list:
  aggregate_list = line.getAggregateValueList()
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Check':
      aggregate.setStopDate(transaction.getStartDate())
      portal_workflow.doActionFor(aggregate,'confirm_action',wf='check_workflow')
