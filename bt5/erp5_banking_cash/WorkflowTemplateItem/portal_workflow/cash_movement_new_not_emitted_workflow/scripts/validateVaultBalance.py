from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

vault = transaction.getSource()
vaultDestination = transaction.getDestination()

# check again that we are in the good accounting date
transaction.Baobab_checkCounterDateOpen(site=vault, date=transaction.getStartDate())

# use of the constraint : Test source and destination
# (Seb) : there is already everything in the checkpath script
vliste = transaction.checkConsistency()
transaction.log('vliste', vliste)
if len(vliste) != 0:
  raise ValidationFailed(vliste[0].getMessage(),)

portal_type_with_no_space = transaction.getPortalType().replace(' ','')
check_path_script = getattr(transaction,'%s_checkPath' % portal_type_with_no_space,None)
if check_path_script is not None:
  message = check_path_script()
  if message is not None:
    raise ValidationFailed(message,)

resource = transaction.CashDelivery_checkCounterInventory(source=vault, portal_type='Cash Movement New Not Emitted Line')


# Get price and total_price.
amount = transaction.getSourceTotalAssetPrice()
total_price = transaction.getTotalPrice(portal_type=['Cash Movement New Not Emitted Line', 'Cash Delivery Cell'],fast=0)

if resource == 2:
  msg = Message(domain="ui", message="No Resource.")
  raise ValidationFailed(msg,)
elif amount != total_price:
  msg = Message(domain="ui", message="Amount differ from total price.")
  raise ValidationFailed(msg,)
elif resource != 0 :
  msg = Message(domain="ui", message="Insufficient Balance.")
  raise ValidationFailed(msg,)
