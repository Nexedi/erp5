if brain.payment_uid:
  brain_list = context.getPortalObject().portal_catalog(uid=brain.payment_uid, limit=2)
  if brain_list:
    brain, = brain_list
    bank_account = brain.getObject()
    # XXX use preference ?
    if bank_account.getReference():
      return '%s - %s' % (bank_account.getReference(), bank_account.getTitle())
    return bank_account.getTitle()
