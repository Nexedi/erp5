"""
  Calculate total price of temporary RAM based Sale Order.

  Price is based on three main components:
    - shopping cart items
    - applicable taxes (based on Person's location and shop's location)
    - shipping costs (same as applicable taxes including type of shopping cart item
      for example online materials doesn't require shipping)

  Script can optionally include currency.
"""

web_site = context.getWebSiteValue()
total = 0.0
shopping_cart_item_list = context.SaleOrder_getShoppingCartItemList(include_shipping)
for order_line in shopping_cart_item_list:
  resource = context.restrictedTraverse(order_line.getResource())
  if order_line.getPrice() is not None:
    total += order_line.getPrice() * order_line.getQuantity()

# XXX: CHECK if we have to include taxes on shipping service
if include_taxes:
  tax_info = context.Person_getApplicableTaxList()
  if tax_info is not None:
    for tax in tax_info.values():
      total += total*(tax['percent']/100)

if include_currency:
  currency = web_site.WebSite_getShoppingCartDefaultCurrency()
  return '%s %s' %(total, currency.getReference())
else:
  return str(total)
