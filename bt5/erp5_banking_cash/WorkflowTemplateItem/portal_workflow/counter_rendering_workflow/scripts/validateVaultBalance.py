from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

vault = transaction.getSource()
date = transaction.getStartDate()

# check we don't change of user
if transaction.getSimulationState() == "draft":
  transaction.Baobab_checkSameUserVault(vault)

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=vault, date=date)

# check counter is opened
site = transaction.getSourceValue()
context.Baobab_checkCounterOpened(site,simulation_state_list=['open', 'closing'])


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
elif resource != 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
