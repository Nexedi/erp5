if brain.payment_uid:
  bank_account = context.getPortalObject().portal_catalog.getObject(brain.payment_uid)
  if bank_account is not None:
    # XXX use preference ?
    if bank_account.getReference():
      return '%s - %s' % (bank_account.getReference(), bank_account.getTitle())
    return bank_account.getTitle()
