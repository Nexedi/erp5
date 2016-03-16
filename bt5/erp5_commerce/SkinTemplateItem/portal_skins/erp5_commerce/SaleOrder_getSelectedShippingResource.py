shopping_cart = context.SaleOrder_getShoppingCart()
shipping_method = getattr(shopping_cart, 'shipping_method', None)
if shipping_method is not None:
  return shipping_method.getResourceValue()
else:
  return None
