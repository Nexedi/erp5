from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

vault = transaction.getSource()

if ('encaisse_des_billets_et_monnaies'  not in vault):
   msg = Message(domain="ui", message="Invalid source.")
   raise ValidationFailed(msg,)

resource = transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Monetary Recall Line')


#source = baobab_source
source_object = context.portal_categories.getCategoryValue(vault)

# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=source_object, date=transaction.getStartDate())

# Get price and total_price.
amount = transaction.getSourceTotalAssetPrice()
total_price = transaction.getTotalPrice(portal_type=['Monetary Recall Line','Cash Delivery Cell'],fast=0)


if resource == 2:
  msg = Message(domain="ui", message="No Resource.")
  raise ValidationFailed(msg,)
elif amount != total_price:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)
elif resource <> 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
