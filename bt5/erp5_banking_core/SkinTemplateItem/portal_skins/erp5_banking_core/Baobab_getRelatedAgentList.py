bank_account = context.getDestinationPaymentValue()

if bank_account in ('', None):
  return []

return bank_account.searchFolder(**kw)
