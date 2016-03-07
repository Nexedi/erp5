reference_currency = context.Baobab_getPortalReferenceCurrencyID()
context.setPriceCurrency('currency_module/%s' %(reference_currency,))
context.setCurrencyExchangeType('transfer')
context.setSource(context.getBaobabSource())

movement = context.newContent(portal_type='Banking Operation Line',
                       id='movement',
                       source='account_module/bank_account', # Set default source
                       destination='account_module/bank_account', # Set default destination
                       )
