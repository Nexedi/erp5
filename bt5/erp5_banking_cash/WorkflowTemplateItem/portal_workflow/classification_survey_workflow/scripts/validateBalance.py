from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

# Purchase Transaction .
transaction = state_change['object']
date = transaction.getStartDate()



# Get inventory
vault = transaction.getSource()
resource =  transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Incoming Classification Survey Line')

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=vault, date=date)

# Get price and total_price.
price = transaction.getSourceTotalAssetPrice()
input_cash = transaction.getTotalPrice(portal_type=['Incoming Classification Survey Line','Cash Delivery Cell'],fast=0)
output_cash = transaction.getTotalPrice(portal_type=['Outgoing Classification Survey Line','Cash Delivery Cell'],fast=0)


if input_cash != output_cash :
  msg=Message(domain="ui", message="Incoming cash amount is different from outgoing cash amount.")
  raise ValidationFailed(msg,)
elif price != output_cash :
  msg=Message(domain='ui',message='Amount differs from cash total.')
  raise ValidationFailed(msg,)
elif resource != 0 :
  msg=Message(domain='ui',message='Insufficient Balance.')
  raise ValidationFailed(msg,)
