from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

# use of the constraint : Test if quantity is multiple of 1000
vliste = transaction.checkConsistency()
if len(vliste) != 0:
  raise ValidationFailed(vliste[0].getMessage(),)

# check again that we are in the good accounting date
vault = transaction.getSource()
transaction.Baobab_checkCounterDateOpen(site=vault, date=transaction.getStartDate())


# Get price and total_price.
price = transaction.getSourceTotalAssetPrice()
input_cash = transaction.getTotalPrice(fast=0,portal_type=('Incoming Cash Sorting Line','Cash Delivery Cell'))
output_cash = transaction.getTotalPrice(fast=0,portal_type=('Outgoing Cash Sorting Line','Outgoing Cash Sorting Cell'))

# Check inventory
resource =  transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Incoming Cash Sorting Line')

if input_cash != output_cash :
  msg=Message(domain="ui", message="Incoming cash amount is different from outgoing cash amount.")
  raise ValidationFailed(msg,)
elif price != output_cash :
  msg=Message(domain='ui',message='Amount differs from cash total.')
  raise ValidationFailed(msg,)
elif resource != 0 :
  msg=Message(domain='ui',message='Insufficient Balance.')
  raise ValidationFailed(msg,)
