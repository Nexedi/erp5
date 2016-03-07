context.setSource(context.getBaobabSource())
reference_currency = context.Baobab_getPortalReferenceCurrencyID()
context.setPriceCurrency('currency_module/%s' %(reference_currency,))
context.setCurrencyExchangeType('sale')
