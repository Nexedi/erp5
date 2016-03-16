resource_id = context.Baobab_getPortalReferenceCurrencyID()

currency_cash_list = [x.getObject() for x in context.currency_cash_module.objectValues() if x.getPortalType() == "Banknote" and x.getObject().getPriceCurrencyId() == resource_id and len(x.getObject().getVariationList())>0]

return [("", None)]+[(x.getTranslatedTitle(), x.getId()) for x in currency_cash_list]
