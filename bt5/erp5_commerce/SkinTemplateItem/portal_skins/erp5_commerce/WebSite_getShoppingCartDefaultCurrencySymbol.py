"""
  Return the sort title of the default currency used in Shopping Cart.
"""
return context.getWebSiteValue().WebSite_getShoppingCartDefaultCurrency().getShortTitle()
