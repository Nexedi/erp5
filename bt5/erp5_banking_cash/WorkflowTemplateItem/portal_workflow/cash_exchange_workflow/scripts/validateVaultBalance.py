from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message
transaction = state_change['object']

currency = transaction.getResourceTitle()
encaisse_billets_et_monnaies_sortante = "/encaisse_des_billets_et_monnaies/sortante"
encaisse_billets_et_monnaies_entrante = "/encaisse_des_billets_et_monnaies/entrante"


counter_site = transaction.getSource()
caisse_incoming = counter_site + encaisse_billets_et_monnaies_entrante
caisse_outgoing = counter_site + encaisse_billets_et_monnaies_sortante

# check we don't change of user
transaction.Baobab_checkSameUserVault(counter_site)

# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=caisse_outgoing, date=transaction.getStartDate())

# check that the counter is open

context.Baobab_checkCounterOpened(counter_site)

# use of the constraint : Test cash status line
#vliste = transaction.checkConsistency()
#transaction.log('vliste', vliste)
#if len(vliste) != 0:
#  raise ValidationFailed, (vliste[0].getMessage(),)


resource_two = transaction.CashDelivery_checkCounterInventory(caisse_outgoing, portal_type='Outgoing Cash Exchange Line')

# Get total_price.
incoming_total = transaction.getTotalPrice(portal_type=['Incoming Cash Exchange Line','Cash Delivery Cell'],fast=0)
outgoing_total = transaction.getTotalPrice(portal_type=['Outgoing Cash Exchange Line','Cash Delivery Cell'],fast=0)


amount_total = transaction.getSourceTotalAssetPrice()

if resource_two == 2:
  msg = Message(domain="ui", message="No resource.")
  raise ValidationFailed(msg,)
elif resource_two == 1:
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)


if incoming_total != outgoing_total:
  msg = Message(domain="ui", message="No same balance.")
  raise ValidationFailed(msg,)

if amount_total != outgoing_total:
  msg = Message(domain="ui", message="Amount not correct.")
  raise ValidationFailed(msg,)
