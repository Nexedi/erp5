from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

delivery = state_change['object']

total_cash = delivery.getTotalPrice(fast=0,portal_type=('Cash Delivery Line','Cash Delivery Cell'))

if len(delivery.objectValues(portal_type="Cash Delivery Line")) == 0:
  msg=Message(domain='ui',message='No resource defined.')
  raise ValidationFailed(msg,)

if total_cash != delivery.getSourceTotalAssetPrice():
  msg=Message(domain='ui',message='Amount differs from cash total.')
  raise ValidationFailed(msg,)

historical_operation_type = delivery.getHistoricalOperationTypeValue()
if historical_operation_type is None:
  msg=Message(domain='ui',message='You must define an historical operation type.')
  raise ValidationFailed(msg,)
