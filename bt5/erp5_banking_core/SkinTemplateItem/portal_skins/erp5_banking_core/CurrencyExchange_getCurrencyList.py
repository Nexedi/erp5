from Products.ERP5Type.Cache import CachingMethod

def getCurrencyList(exclude_reference_currency=0):
  currency_value_list = context.currency_module.objectValues()
  if exclude_reference_currency:
    reference_id = context.Baobab_getPortalReferenceCurrencyID()
    currency_value_list = [x for x in currency_value_list if x.getId() != reference_id]
  currency_list = [('%s - %s' % (x.getReference(), x.getTitle()), x.getRelativeUrl())
    for x in currency_value_list]

  currency_list.insert(0, ('',''))
  return currency_list

getCurrencyList = CachingMethod(getCurrencyList, id = 'CurrencyExchange_getCurrencyList', 
                                cache_factory = "erp5_ui_medium")
return getCurrencyList(exclude_reference_currency=exclude_reference_currency)
