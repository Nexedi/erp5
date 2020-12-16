"""
  Return list of shopping cart items.
  XXX : get order_line as tree not just on first level
"""
shopping_cart = context.SaleOrder_getShoppingCart()
if not shopping_cart:
  return []
shopping_cart_order_lines = shopping_cart.contentValues()
if include_shipping:
  return shopping_cart_order_lines
else:
  return filter(lambda x: x.getId()!='shipping_method', shopping_cart_order_lines)
