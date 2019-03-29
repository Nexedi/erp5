"""Set connected user as shopping cart customer"""
if REQUEST is not None:
  raise RuntimeError("You can not call this script from the URL")

shopping_cart = context.SaleOrder_getShoppingCart()

if person is None:
  person = shopping_cart.SaleOrder_getShoppingCartCustomer()

shopping_cart.edit(destination_decision_value=person)
