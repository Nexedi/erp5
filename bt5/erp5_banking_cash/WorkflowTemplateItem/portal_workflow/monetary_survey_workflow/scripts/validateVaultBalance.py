from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
date = transaction.getStartDate()
vault = transaction.getSource()
destination = transaction.getDestination()

if vault is None or destination is None:
   msg = Message(domain="ui", message="You must define source and destination.")
   raise ValidationFailed(msg,)
   

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=vault, date=date)

if ('encaisse_des_billets_et_monnaies'  not in vault) and ('encaisse_des_billets_a_ventiler_et_a_detruire' not in vault):
   msg = Message(domain="ui", message="Invalid source.")
   raise ValidationFailed(msg,)

if ('encaisse_des_billets_et_monnaies'  not in destination) and ('encaisse_des_billets_a_ventiler_et_a_detruire' not in destination):
   msg = Message(domain="ui", message="Invalid destination.")
   raise ValidationFailed(msg,)

if ('encaisse_des_billets_et_monnaies'  in vault) and ('encaisse_des_billets_a_ventiler_et_a_detruire' not in destination):
   msg = Message(domain="ui", message="Impossible Monetary Survey.")
   raise ValidationFailed(msg,)

if ('encaisse_des_billets_a_ventiler_et_a_detruire'  in vault) and ('encaisse_des_billets_et_monnaies' not in destination):
   msg = Message(domain="ui", message="Impossible Monetary Survey Reintregration.")
   raise ValidationFailed(msg,)

resource = transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Cash Delivery Line')
# Get price and total_price.
amount = transaction.getSourceTotalAssetPrice()
total_price = transaction.getTotalPrice(portal_type=['Cash Delivery Line','Cash Delivery Cell'],fast=0)

if resource == 2:
  msg = Message(domain="ui", message="No Resource.")
  raise ValidationFailed(msg,)
elif amount != total_price:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)
elif resource <> 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
