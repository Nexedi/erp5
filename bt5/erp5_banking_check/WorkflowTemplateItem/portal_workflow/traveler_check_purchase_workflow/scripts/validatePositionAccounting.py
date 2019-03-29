from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

transaction = state_change['object']

date = transaction.getStartDate()
source = transaction.getSource(None)
if source is None:
  msg = Message(domain='ui', message='No counter defined.')
  raise ValidationFailed(msg,)

# check we don't change of user
transaction.Baobab_checkSameUserVault(source)

# check we are in an opened accounting day
transaction.Baobab_checkCounterDateOpen(site=source, date=date)

context.Baobab_checkCounterOpened(source)

# First we have to look if we have some checks with some prices,
# if so, this means that we are saling such kinds of check, thus
# we must change the position of the customer account
movement_list = transaction.getMovementList()
total_credit = 0
for movement in movement_list:
  aggregate_value_list = movement.getAggregateValueList()
  for item in aggregate_value_list:
    if item.getPortalType()=='Check':
      if item.getSimulationState()!='confirmed':
        msg = Message(domain = "ui", message="Sorry, one traveler check was not sale yet")
        raise ValidationFailed(msg,)
      if item.getPrice() is not None:
        # then we must calculate the exchange value at the
        # time where the item was first delivered
        category_list = movement.getCategoryList()
        base_price = transaction.CurrencyExchange_getExchangeRateList(
                                    from_currency=item.getPriceCurrency(),
                                    to_currency='currency_module/%s' % context.Baobab_getPortalReferenceCurrencyID(),
                                    currency_exchange_type='transfer',
                                    start_date=item.getStartDate())[0]
        if base_price is None:
          msg = Message(domain = "ui", message="Sorry, no valid price was found for this currency")
          raise ValidationFailed(msg,)
        total_credit += base_price*item.getPrice()
      else:
        msg = Message(domain = "ui", message="Sorry, the price was not defined on some traveler checks")
        raise ValidationFailed(msg,)

if total_credit>0:
  total_credit = round(total_credit,0)
  # Source and destination will be updated automaticaly based on the category of bank account
  # The default account chosen should act as some kind of *temp* account or *parent* account
  movement = transaction.get('movement',None)
  if movement is None:
    movement = transaction.newContent(portal_type='Banking Operation Line',
                           id='movement',
                           source='account_module/bank_account', # Set default source
                           destination='account_module/bank_account', # Set default destination
                           )
  movement.setSourceCredit(total_credit)
  transaction.setSourceTotalAssetPrice(total_credit)
