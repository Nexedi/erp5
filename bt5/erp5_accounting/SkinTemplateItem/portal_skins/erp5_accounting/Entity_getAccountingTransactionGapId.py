if None not in (brain, selection):
  try:
    account_uid = brain.account_uid
  except AttributeError:
    account_uid = None
  if account_uid != None:
    account = context.portal_catalog.getObject(account_uid)
    if account != None:
      return account.Account_getGapId()
return None
