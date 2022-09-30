"""
  Update shopping cart by change items quantity and setting preferred
  shipping.
"""

request = context.REQUEST
translateString = context.Base_translateString
quantity = field_my_buy_quantity
shipping_method =  field_my_shipping_method
shopping_cart_items = context.SaleOrder_getShoppingCartItemList(include_shipping=True)
shopping_cart_products_items = filter(lambda x: x.getId()!='shipping_method', shopping_cart_items)
shopping_cart = context.SaleOrder_getShoppingCart()

# handle change in quantity for shopping items
if quantity is not None:
  # when we have one item in shoppping cart we get
  # quantity as a string rather as a list
  if isinstance(quantity, str):
    quantity = [quantity]

  counter = 0
  for order_line in shopping_cart_products_items:
    new_quantity = int(quantity[counter])
    if new_quantity>=1:
      order_line.setQuantity(new_quantity)
    else:
      # remove it from shopping cart
      shopping_cart.manage_delObjects(order_line.getId())
    counter += 1

# handle shipping
order_line = getattr(shopping_cart, 'shipping_method', None)
if shipping_method not in ['', None]:
  shipping = context.getPortalObject().restrictedTraverse(shipping_method)
  if order_line is None:
    # create new shipping method order line
    order_line = shopping_cart.newContent(id='shipping_method', portal_type='Sale Order Line')
  # .. and update it
  order_line.setResource(shipping.getRelativeUrl())
  order_line.setQuantity(1)
else:
  if field_my_shipping_method in ['', None] and order_line is not None:
    shopping_cart.manage_delObjects(order_line.getId())

return context.SaleOrder_paymentRedirect(field_my_comment, field_my_payment_mode)
