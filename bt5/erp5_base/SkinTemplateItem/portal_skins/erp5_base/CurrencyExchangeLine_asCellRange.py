currency_exchange_type_list = context.portal_categories.currency_exchange_type.getCategoryChildRelativeUrlList()
resource_list = ['resource/%s' % context.getParentValue().getRelativeUrl()]
price_currency_list = [context.getPriceCurrency(base=True)]

return (currency_exchange_type_list, resource_list, price_currency_list)
