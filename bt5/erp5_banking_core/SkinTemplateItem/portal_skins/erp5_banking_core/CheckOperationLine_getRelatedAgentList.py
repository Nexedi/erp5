bank_account = context.getSourcePaymentValue()

if bank_account in ('', None):
  return []

return bank_account.searchFolder()
