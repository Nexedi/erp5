from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
date = transaction.getStartDate()
vault = transaction.getSource()
vaultDestination = transaction.getDestination()

if vault is None or vaultDestination is None:
  msg = Message(domain="ui", message="You must define vaults.")
  raise ValidationFailed(msg,)

# use of the constraint : Test source and destination
vliste = transaction.checkConsistency()
transaction.log('vliste', vliste)
if len(vliste) != 0:
  raise ValidationFailed(vliste[0].getMessage(),)

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=vaultDestination, date=date)


if 'reserve' in vault and 'salle_tri' in vaultDestination:
  msg = Message(domain="ui", message="Cannot transfer ressource to ${destination} from ${source}.",
                mapping={'source':transaction.getSourceValue().getParentValue().getTitle(),
                         'destination':transaction.getDestinationValue().getParentValue().getTitle()})

  raise ValidationFailed(msg,)
resource = transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Vault Transfer Line')

# Get price and total_price.
amount = transaction.getSourceTotalAssetPrice()
total_price = transaction.getTotalPrice(portal_type=['Vault Transfer Line','Vault Transfer Cell'],fast=0)

if resource == 2:
  msg = Message(domain="ui", message="No Resource.")
  raise ValidationFailed(msg,)
elif amount != total_price:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)
elif resource <> 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
