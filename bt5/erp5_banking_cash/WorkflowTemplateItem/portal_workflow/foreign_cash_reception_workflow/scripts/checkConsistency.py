from Products.ERP5Type.Message import Message
from Products.DCWorkflow.DCWorkflow import ValidationFailed

object = state_change['object']

transaction = state_change['object']

# use of the constraint
vliste = object.checkConsistency()
object.log('vliste', vliste)
if len(vliste) != 0:
  raise ValidationFailed(vliste[0].getMessage(),)

dest = object.getDestination()
# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=dest, date=transaction.getStartDate())
if not 'encaisse_des_devises' in object.getDestination():
  msg = Message(domain="ui", message="Wrong Destination Selected.")
  raise validationFailed(msg,)

object_price = object.getSourceTotalAssetPrice()
line_price = object.getTotalPrice(portal_type=['Cash Delivery Line','Cash Delivery Cell'],fast=0)

if object_price != line_price:
  msg = Message(domain="ui", message="Amount differs between document and lines.")
  raise ValidationFailed(msg,)
