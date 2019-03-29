from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

aggregate_uid_list = [
  x.uid for x in context.portal_simulation.getCurrentTrackingList(
    at_date=at_date,
    node=node_url,
    item_catalog_portal_type=('Check', 'Checkbook'),
  )
]
for line in context.getMovementList():
  for aggregate_value in line.getAggregateValueList():
    if aggregate_value.getUid() not in aggregate_uid_list:
      reference = aggregate_value.getReference()
      if reference is None:
        reference = '%s - %s' % (aggregate_value.getReferenceRangeMin() or '', aggregate_value.getReferenceRangeMax() or '')
      msg = Message(domain="ui", message="Sorry, the item with reference $reference is not available any more",
                    mapping={'reference':reference})
      raise ValidationFailed(msg,)
