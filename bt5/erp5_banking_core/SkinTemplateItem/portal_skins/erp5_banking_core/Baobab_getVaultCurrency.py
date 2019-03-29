# This script will try to guess what is the current currency
# for the particular vault

vault_list = vault.split('/')
currency_id = None
# Well, this is not a nice way of doing, we should have
# a mapping or something instead
if 'encaisse_des_devises' in vault_list:
  vault_currency_title = vault_list[vault_list.index('encaisse_des_devises')+1]
  context.log('Baobab_getVaultCurrency, vault = ', vault_currency_title)
  for currency in context.currency_module.objectValues():
    context.log('Baobab_getVaultCurrency, cur = ', currency.getTitle())
    currency_title = currency.getTitle().replace(' ','_').lower()
    if currency_title == vault_currency_title:
      return currency.getRelativeUrl()
else:
  return context.currency_module[context.Baobab_getPortalReferenceCurrencyID()].getRelativeUrl()

raise ValueError('No currency found for vault %s'  %vault)
