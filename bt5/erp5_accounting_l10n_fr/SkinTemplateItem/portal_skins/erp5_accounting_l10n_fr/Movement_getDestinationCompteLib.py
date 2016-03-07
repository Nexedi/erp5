account = context.getDestinationValue(portal_type='Account')

if account.isMemberOf('account_type/asset/cash/bank'):
  return "%s - %s" % (account.getTranslatedTitle(), context.getDestinationPaymentTitle())

return account.getTranslatedTitle()
