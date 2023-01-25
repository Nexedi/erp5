"""
  Return the default trade condition for thie ecommerce site
"""
return context.getWebSiteValue().getLayoutProperty(
                                      'ecommerce_default_trade_condition',
                                      'sale_trade_condition_module/default_trade_condition')
