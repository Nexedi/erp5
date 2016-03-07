"""Get the shopping cart customer"""
shopping_cart = context.SaleOrder_getShoppingCart()
result = shopping_cart.getDestinationSectionValue()
if result is None:
  shopping_cart.SaleOrder_setShoppingCartCustomer()
  result = shopping_cart.getDestinationSectionValue()

return result
