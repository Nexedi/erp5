from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
date = transaction.getStartDate()
source = transaction.getSource(None)


# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=source, date=transaction.getStartDate())


# check again that the counter is open

context.Baobab_checkCounterOpened(source)

if transaction.getPaymentType() in (None, ""):
  msg = Message(domain="ui", message="No payment type defined.")
  raise ValidationFailed(msg,)


#test if the source or the destination is correct
transaction.Base_checkBaobabSourceAndDestination()

# Get price and total_price.
amount = transaction.getSourceTotalAssetPrice()
total_price = transaction.getTotalPrice(portal_type=('Cash Delivery Line','Cash Delivery Cell'), fast=0)

if amount != total_price:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)

if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)



site = transaction.getSourceValue()



vault = transaction.getBaobabSource()
resource = transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Cash Delivery Line',same_source=1)

#context.log('resource',resource)

if resource == 2:
  msg = Message(domain="ui", message="No Resource.")
  raise ValidationFailed(msg,)
