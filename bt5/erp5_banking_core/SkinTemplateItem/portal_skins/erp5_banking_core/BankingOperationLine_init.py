context.edit(quantity_unit = 'unit',
             source = 'account_module/bank_account',
             destination = 'account_module/bank_account',
             resource = 'currency_module/%s' % context.Baobab_getPortalReferenceCurrencyID())
