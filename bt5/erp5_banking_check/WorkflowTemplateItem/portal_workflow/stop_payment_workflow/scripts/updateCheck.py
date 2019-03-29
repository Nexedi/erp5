# We will make sure that the check will not be usable
transaction = state_change['object']
from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

portal_workflow = transaction.portal_workflow

aggregate_list = []
line_list = transaction.getMovementList()
for line in line_list:
  aggregate_list.extend(line.getAggregateValueList())
ref_min = transaction.getReferenceRangeMin()
ref_max = transaction.getReferenceRangeMin()
if ref_min is not None or ref_max is not None:
  if len(aggregate_list)==0:
    msg = Message(domain='ui', message='Sorry, no check was found, but there is a reference.')
    raise ValidationFailed(msg,)
  for aggregate in aggregate_list:
    if aggregate.getPortalType()=='Check':
      aggregate.setStopDate(transaction.getStartDate())
      portal_workflow.doActionFor(aggregate,'stop_action',wf='check_workflow')
