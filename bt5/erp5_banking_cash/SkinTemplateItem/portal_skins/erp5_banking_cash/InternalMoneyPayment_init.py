# create a default banking operation line that will be updated later
#context.edit(external_software='star')

transaction = context

context.setSource('%s/encaisse_des_billets_et_monnaies/sortante' % (context.Baobab_getUserAssignedSiteList()[0], ))

# XXX it might be better to set resource according to source_payment.
transaction.setResource('currency_module/' + context.Baobab_getPortalReferenceCurrencyID())

movement = context.newContent(portal_type='Banking Operation Line',
                       id='movement',
                       source='account_module/bank_account', # Set default source
                       destination='account_module/bank_account', # Set default destination
                       )
