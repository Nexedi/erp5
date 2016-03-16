account = context.getSourceValue(portal_type='Account')

if account.isMemberOf('account_type/asset/cash/bank'):
  return "%s - %s" % (account.getTranslatedTitle(), context.getSourcePaymentTitle())

return account.getTranslatedTitle()
