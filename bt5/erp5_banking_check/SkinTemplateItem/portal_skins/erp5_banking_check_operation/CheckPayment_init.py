transaction = context

# XXX it might be better to set resource according to source_payment.
transaction.setResource('currency_module/' + context.Baobab_getPortalReferenceCurrencyID())

movement = transaction.newContent(portal_type='Banking Operation Line',
                       id='movement',
                       source='account_module/bank_account', # Set default source
                       destination='account_module/bank_account', # Set default destination
                       )
# Source and destination will be updated automaticaly based on the category of bank account
# The default account chosen should act as some kind of *temp* account or *parent* account
