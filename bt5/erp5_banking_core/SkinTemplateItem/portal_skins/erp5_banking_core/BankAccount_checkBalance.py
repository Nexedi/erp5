# check that the amount of `resource` in account `payment` is greater than or equal to `quantity`
# returns a dictionnary like : {'error_code', 'balance'}

# First check that the payment account is in an acceptable state
payment_value = context.restrictedTraverse(payment)

if not payment_value.BankAccount_isOpened():
  return {'error_code': 2} # closed account

account_balance = payment_value.BankAccount_getAvailablePosition(src__=src__)
if src__:
  return account_balance
# XXX: BankAccount_getAvailablePosition returns position as a string for some reason...
raw_account_balance = account_balance = float(account_balance)
if round_balance:
  account_balance = round(account_balance, payment_value.getPriceCurrencyValue().getQuantityPrecision())

if account_balance - quantity < 0:
  # insufficient balance
  return {
    'error_code': 1,
    'balance': account_balance,
    'raw_balance': raw_account_balance,
  }

payment_value.serialize()
return {
  'error_code': 0,
  'balance': account_balance,
  'raw_balance': raw_account_balance,
}
