from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

date = transaction.getStartDate()
from DateTime import DateTime
now = DateTime()

source = transaction.getSource(None)
if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)

# No need for stop payment to check the counter date
#if not transaction.Baobab_checkCounterDateOpen(site=source, date=date):
#  msg = Message(domain = "ui", message="Counter Date is not opened")
#  raise ValidationFailed, (msg,)

ref_min = transaction.getReferenceRangeMin()
ref_max = transaction.getReferenceRangeMax()

# We will first retrieve all checks
check_list = []
if ref_min is not None or ref_max is not None:
  aggregate_resource = transaction.getAggregateResource()
  check_list = transaction.Base_checkOrCreateCheck(
                          reference_range_min = ref_min,
                          reference_range_max = ref_max,
                          resource=aggregate_resource)
if len(check_list)>0:
  # First make sure there is no delivery line
  line_list = transaction.objectValues(portal_type='Checkbook Delivery Line')
  if len(line_list)>0:
    id_list = [x.getId() for x in line_list]
    transaction.manage_delObjects(ids=id_list)

  # Then we will construct a new line for each check
  for item in check_list:
    delivery_line = transaction.newContent(portal_type='Checkbook Delivery Line')
    item_dict = {}
    reference_range_min = None
    reference_range_max = None
    if item.getPortalType()=='Check':
      reference_range_min = reference_range_max = item.getReference()
    item_dict['reference_range_min'] = reference_range_min
    item_dict['reference_range_max'] = reference_range_max
    item_dict['destination_trade'] = item.getDestinationTrade()
    item_dict["resource_value"] = item.getResourceValue()
    item_dict["check_amount"] = item.getCheckAmount()
    item_dict["check_type"] = item.getCheckType()
    item_dict["price_currency"] = item.getPriceCurrency()
    item_dict["aggregate_value"] = item
    item_dict["quantity"] = 1
    delivery_line.edit(**item_dict)

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
    if item.getSimulationState()!='confirmed':
      msg = Message(domain = "ui", message="Sorry, this check is not issued")
      raise ValidationFailed(msg,)
    # Test check is valid based on date
    transaction.Check_checkIntervalBetweenDate(resource=item.getResourceValue(),
                                             start_date=date,
                                             stop_date=now,
                                             check_nb=item.getTitle())


debit_required = transaction.isDebitRequired()
if total_debit in (None,0.0) and debit_required:
  msg = Message(domain = "ui", message="Sorry, you forgot to give the amount")
  raise ValidationFailed(msg,)
if debit_required:
  # Source and destination will be updated automaticaly based on the category of bank account
  # The default account chosen should act as some kind of *temp* account or *parent* account
  movement = transaction.get('movement',None)
  if movement is None:
    movement = transaction.newContent(portal_type='Banking Operation Line',
                           id='movement',
                           source='account_module/bank_account', # Set default source
                           destination='account_module/bank_account', # Set default destination
                           )
  movement.setSourceDebit(total_debit)
  transaction.setSourceTotalAssetPrice(total_debit)

  line = transaction.movement
  bank_account = transaction.getDestinationPaymentValue()

  # this prevents multiple transactions from being committed at the same time for this bank account.
  bank_account.serialize()

  # Make sure there are no other operations pending for this account
  if transaction.BankAccount_isMessagePending(bank_account):
    msg = Message(domain='ui', message="There are operations pending for this account that prevent form calculating its position. Please try again later.")
    raise ValidationFailed(msg,)

  # Index the banking operation line so it impacts account position
  transaction.BankingOperationLine_index(line)

  # Test if the account balance is sufficient.
  error = transaction.BankAccount_checkBalance(bank_account.getRelativeUrl(), total_debit)
  if error['error_code'] == 1:
    msg = Message(domain='ui', message="Bank account is not sufficient.")
    raise ValidationFailed(msg,)
  elif error['error_code'] == 2:
    msg = Message(domain='ui', message="Bank account is not valid.")
    raise ValidationFailed(msg,)
  elif error['error_code'] != 0:
    msg = Message(domain='ui', message="Unknown error code.")
    raise ValidationFailed(msg,)
