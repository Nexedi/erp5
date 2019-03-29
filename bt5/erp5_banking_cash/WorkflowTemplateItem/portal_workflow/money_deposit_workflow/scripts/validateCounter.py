from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']
date = transaction.getStartDate()
destination= transaction.getDestination(None)
transaction.log('destination:',destination)

amount = transaction.getSourceTotalAssetPrice()
if amount is None:
  msg = Message(domain="ui", message="Sorry, you have to define a quantity.")
  raise ValidationFailed(msg,)

destination_payment = transaction.getDestinationPayment()
if destination_payment is None:
  msg = Message(domain="ui", message="Sorry, you have to define an account.")
  raise ValidationFailed(msg,)

var_state = transaction.getSimulationState()
if var_state == 'confirmed': 
  # Get price and total_price.
  amount = transaction.getSourceTotalAssetPrice()
  total_price = transaction.getTotalPrice(portal_type='Cash Delivery Cell')

  if amount != total_price:
    msg = Message(domain="ui", message="Amount differ from total price.")
    raise ValidationFailed(msg,)

if destination is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)


# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=destination, date=transaction.getStartDate())
if transaction.getSimulationState() == "ordered":
  transaction.Baobab_checkCounterOpened(destination)

site = transaction.getDestinationValue()
# I comment theses lines, because it's not necessary to control if all counter is opened or not at the moment : CISSE
# check that the counter is opened
#counter_list = [x.getObject() for x in transaction.portal_catalog(portal_type="Counter", simulation_state = 'open', site_uid = site.getUid())]

#if len(counter_list) == 0:
#  msg = Message(domain = "ui", message="Counter is not opened")
#  raise ValidationFailed, (msg,)
