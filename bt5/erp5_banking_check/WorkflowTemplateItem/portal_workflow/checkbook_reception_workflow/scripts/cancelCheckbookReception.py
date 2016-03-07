delivery = state_change['object']

# Make sure to delete what was already created
for line in delivery.objectValues(portal_type='Checkbook Reception Line'):
  for aggregate in line.getAggregateValueList():
    if aggregate.portal_type == 'Checkbook':
      for check in aggregate.objectValues():
        delivery.portal_workflow.doActionFor(check, 'delete_action')
    delivery.portal_workflow.doActionFor(aggregate, 'delete_action')
