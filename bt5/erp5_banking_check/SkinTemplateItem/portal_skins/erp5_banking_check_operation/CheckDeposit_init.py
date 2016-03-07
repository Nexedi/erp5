transaction = context

user_site = context.Baobab_getUserAssignedRootSite()
context.setSite(user_site)

# XXX it might be better to set resource according to source_payment.
transaction.setResource('currency_module/' + context.Baobab_getPortalReferenceCurrencyID())
