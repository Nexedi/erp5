reference_currency = context.Baobab_getPortalReferenceCurrencyID()

currency_list = [('%s - %s' % (x.getId(), x.getTitle()), x.getRelativeUrl())
  for x in context.currency_module.objectValues()
  if x.getId() != reference_currency]

currency_list.insert(0, ('',''))

return currency_list
