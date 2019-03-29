from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

source = transaction.getBaobabSource()
destination = transaction.getBaobabDestination()
msg = None
if source == destination:
  msg = Message(domain="ui", message="Sorry, the source and the destination must be different")

line_list = transaction.objectValues()
if len(line_list)==0:
  msg = Message(domain="ui", message="Sorry, you must select at least one check or checkbook")

at_date = transaction.getStartDate()
transaction.CheckbookDelivery_checkAggregateStockList(at_date=at_date, node_url = source)

if msg is not None:
  raise ValidationFailed(msg,)
