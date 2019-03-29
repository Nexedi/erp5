from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

date = transaction.getStartDate()
source = transaction.getSource(None)
if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)

# No need to check the counter date for stop payment
#if not transaction.Baobab_checkCounterDateOpen(site=source, date=date):
#  msg = Message(domain = "ui", message="Counter Date is not opened")
#  raise ValidationFailed, (msg,)

# First we have to look if we have some checks with some prices,
# if so, this means that we are saling such kinds of check, thus
# we must change the position of the customer account
movement_list = transaction.getMovementList()
total_debit = transaction.getSourceTotalAssetPrice()
for movement in movement_list:
  aggregate_value_list = movement.getAggregateValueList()
  for item in aggregate_value_list:
    if item.getPortalType()!='Check':
      msg = Message(domain = "ui", message="Sorry, You should select a check")
      raise ValidationFailed(msg,)
    if item.getSimulationState()!='stopped':
      msg = Message(domain = "ui", message="Sorry, this check is not stopped")
      raise ValidationFailed(msg,)
debit_required = transaction.isDebitRequired()
if debit_required:
  if transaction.getSimulationState() == 'started':
    stop_date = state_change.kwargs.get('stop_date')
    if stop_date is None:
      msg = Message(domain = "ui", message="No stop date provided")
      raise ValidationFailed(msg,)
    transaction.setStopDate(stop_date)

  # Source and destination will be updated automaticaly based on the category of bank account
  # The default account chosen should act as some kind of *temp* account or *parent* account
  movement = transaction.get('lift_movement',None)
  if movement is None:
    movement = transaction.newContent(portal_type='Banking Operation Line',
                           id='lift_movement',
                           source='account_module/bank_account', # Set default source
                           destination='account_module/bank_account', # Set default destination
                           )
  movement.setSourceCredit(total_debit)

  bank_account = transaction.getDestinationPaymentValue()
