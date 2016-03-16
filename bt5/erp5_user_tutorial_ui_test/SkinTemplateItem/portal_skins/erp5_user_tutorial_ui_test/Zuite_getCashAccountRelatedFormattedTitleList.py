cash = context.portal_categories.account_type.asset.cash
account_type_related_list = cash.getAccountTypeRelatedValueList(portal_type='Account')

return [x.Account_getFormattedTitle() for x in account_type_related_list]
