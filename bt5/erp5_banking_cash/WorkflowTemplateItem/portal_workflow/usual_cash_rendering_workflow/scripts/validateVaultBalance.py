from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
date = transaction.getStartDate()
vault = transaction.getSource()
vaultDestination = transaction.getDestination()

# use of the constraint
vliste = transaction.checkConsistency()
if len(vliste) != 0:
  raise ValidationFailed(vliste[0].getTranslatedMessage(),)

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=vault, date=date)

if 'reserve' in vault and 'salle_tri' in vaultDestination:
  msg = Message(domain="ui", message="Cannot transfer ressource to ${destination} from ${source}.",
                mapping={'source':transaction.getSourceValue().getParentValue().getTitle(),
                         'destination':transaction.getDestinationValue().getParentValue().getTitle()})

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
elif resource != 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
