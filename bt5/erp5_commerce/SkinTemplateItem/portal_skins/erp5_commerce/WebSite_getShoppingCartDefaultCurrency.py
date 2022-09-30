"""
  Return default currency used in Shopping Cart.
"""
web_site = context.getWebSiteValue()
return context.getPortalObject().restrictedTraverse(web_site.getLayoutProperty('ecommerce_base_currency', 'currency_module/EUR'))
