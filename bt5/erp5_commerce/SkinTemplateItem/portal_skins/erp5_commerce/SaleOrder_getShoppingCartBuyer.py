"""Get the shopping cart customer"""
shopping_cart = context.SaleOrder_getShoppingCart()
return shopping_cart.getDestinationDecisionValue()
