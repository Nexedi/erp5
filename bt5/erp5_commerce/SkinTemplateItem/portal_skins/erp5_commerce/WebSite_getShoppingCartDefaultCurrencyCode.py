"""
  Return reference of the default currency used in Shopping Cart.
"""
website = context.getWebSiteValue()
if website:
  return website.WebSite_getShoppingCartDefaultCurrency().getReference()
else:
  return ''
