from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

date = transaction.getStartDate()
destination= transaction.getDestination()
# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=destination, date=transaction.getStartDate())

site = transaction.getDestinationValue()

# check again that the counter is open

context.Baobab_checkCounterOpened(destination)

if transaction.getResource() is None:
  msg = Message(domain="ui", message="No resource defined.")
  raise ValidationFailed(msg,)

# Check getBaobabSource and getBaobabDestination
#transaction.Base_checkBaobabSourceAndDestination()


# check we don't change of user
transaction.Baobab_checkSameUserVault(destination)

lettering = transaction.getGroupingReference()

if lettering is None:
  msg = Message(domain='ui', message='No lettering defined.')
  raise ValidationFailed(msg,)

if destination is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)



# Get price and total_price.
price = transaction.getSourceTotalAssetPrice()
cash_detail = transaction.getTotalPrice(portal_type = ['Cash Delivery Line', 'Cash Delivery Cell'], fast=0)

if price != cash_detail:
  msg = Message(domain="ui", message="Amount differs from input.")
  raise ValidationFailed(msg,)
