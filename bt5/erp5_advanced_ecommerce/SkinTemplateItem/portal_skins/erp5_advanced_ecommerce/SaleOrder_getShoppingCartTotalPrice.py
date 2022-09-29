"""
  Calculate total price of temporary RAM based Sale Order.

  Price is based on three main components:
    - shopping cart items
    - shipping costs (same as applicable taxes including type of shopping cart item
      for example online materials doesn't require shipping)

  Script can optionally include currency.
"""
web_site = context.getWebSiteValue()
total = 0.0
sale_order = context.SaleOrder_getShoppingCart()
if sale_order is None:
  return total

if discount:
  total = sale_order.SaleOrder_getFinalPrice()
else:
  total = sale_order.getTotalPrice()

if not include_shipping:
  shipping_method = getattr(sale_order, 'shipping_method', None)
  if shipping_method is not None:
    total -= shipping_method.getTotalPrice()

if include_currency:
  currency = web_site.WebSite_getShoppingCartDefaultCurrency()
  return '%s %s' % (total, currency.getReference())
else:
  return str(total)
