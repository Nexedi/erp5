"""
  Return list of shopping cart items.
  XXX : get order_line as tree not just on first level
"""
shopping_cart_order_lines = context.SaleOrder_getShoppingCart().contentValues()
if include_shipping:
  return shopping_cart_order_lines
else:
  return filter(lambda x: x.getId()!='shipping_method', shopping_cart_order_lines)
