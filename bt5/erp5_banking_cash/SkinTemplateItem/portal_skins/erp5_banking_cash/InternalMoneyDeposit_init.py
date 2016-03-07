context.setResource('currency_module/' + context.Baobab_getPortalReferenceCurrencyID())

context.setDestination(context.getBaobabDestination())

movement = context.newContent(portal_type='Banking Operation Line',
                       id='movement',
                       source='account_module/bank_account', # Set default source
                       destination='account_module/bank_account', # Set default destination
                       )
