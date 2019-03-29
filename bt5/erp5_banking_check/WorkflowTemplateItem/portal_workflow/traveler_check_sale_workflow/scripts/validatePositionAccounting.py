from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

# check we have defined an account
if transaction.getDestinationPayment() is None:
  msg = Message(domain = "ui", message="Sorry, no account selected")
  raise ValidationFailed(msg,)

# First we have to look if we have some checks with some prices,
# if so, this means that we are saling such kinds of check, thus
# we must change the position of the customer account
movement_list = transaction.getMovementList()
total_debit = 0
for movement in movement_list:
  aggregate_value_list = movement.getAggregateValueList()
  for item in aggregate_value_list:
    if item.getSimulationState()!='draft':
      msg = Message(domain = "ui", message="Sorry, one traveler check was already saled")
      raise ValidationFailed(msg,)
    if item.getPortalType()=='Check':
      if item.getPrice() is not None:
        # then we must calculate the exchange value
        category_list = movement.getCategoryList()
        base_price = transaction.CurrencyExchange_getExchangeRateList(
                                    from_currency=item.getPriceCurrency(),
                                    to_currency='currency_module/%s' % context.Baobab_getPortalReferenceCurrencyID(),
                                    currency_exchange_type='transfer')[0]
        if base_price is None:
          msg = Message(domain = "ui", message="Sorry, no valid price was found for this currency")
          raise ValidationFailed(msg,)
        total_debit += base_price*item.getPrice()
      else:
        msg = Message(domain = "ui", message="Sorry, the price was not defined on some traveler checks")
        raise ValidationFailed(msg,)
if total_debit>0:
  total_debit = round(total_debit)
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

  if bank_account is None:
    msg = Message(domain='ui', message="Sorry, no account defined.")
    raise ValidationFailed(msg,)

  price = total_debit

  # this prevents multiple transactions from being committed at the same time for this bank account.
  bank_account.serialize()

  # Make sure there are no other operations pending for this account
  if context.BankAccount_isMessagePending(bank_account):
    msg = Message(domain='ui', message="There are operations pending for this account that prevent form calculating its position. Please try again later.")
    raise ValidationFailed(msg,)

  # Index the banking operation line so it impacts account position
  context.BankingOperationLine_index(line)

  # Test if the account balance is sufficient.
  error = transaction.BankAccount_checkBalance(bank_account.getRelativeUrl(), price)
  if error['error_code'] == 1:
    msg = Message(domain='ui', message="Bank account is not sufficient.")
    raise ValidationFailed(msg,)
  elif error['error_code'] == 2:
    msg = Message(domain='ui', message="Bank account is not valid.")
    raise ValidationFailed(msg,)
  elif error['error_code'] != 0:
    msg = Message(domain='ui', message="Unknown error code.")
    raise ValidationFailed(msg,)

if total_debit==0:
  msg = Message(domain='ui', message='Please select at least one traveler check.')
  raise ValidationFailed(msg,)

date = transaction.getStartDate()
source = transaction.getSource(None)
if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=source, date=date)

site = transaction.getSourceValue()

context.Baobab_checkCounterOpened(site)
