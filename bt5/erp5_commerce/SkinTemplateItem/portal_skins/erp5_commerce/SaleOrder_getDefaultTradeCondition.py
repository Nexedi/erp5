"""Return the default trade condition"""
default = "sale_trade_condition_module/default_trade_condition"

website = context.getWebSiteValue()
if website:
  default = website.getLayoutProperty('ecommerce_default_trade_condition', default)

return context.getPortalObject().restrictedTraverse(default)
