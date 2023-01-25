"""
  Update shopping cart by changing item quantities and by setting preferred
  shipping method and payment method.

  TODO:
  - support modern payment conditions (instead of payment_mode)
  - use Base_edit and a real ERP5 Form in order to  benefit from
    field reusability and property validation
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString
if field_my_buy_quantity is None:
  field_my_buy_quantity = context.REQUEST.get("field_my_buy_quantity", None)

if field_my_shipping_method is None:
  field_my_shipping_method=context.REQUEST.get("field_my_shipping_method", None)

if field_my_payment_mode is None:
  field_my_payment_mode = context.REQUEST.get("field_my_payment_mode", None)

quantity = field_my_buy_quantity

shopping_cart = context.SaleOrder_getShoppingCart()
shopping_cart_product_item_list = context.SaleOrder_getShoppingCartItemList()

# Handle change in quantity for shopping items
if quantity is not None:
  # Whenever there is only one item in shoppping cart, quantity
  # is a string rather as a list
  if isinstance(quantity, str):
    quantity = [quantity]

  counter = 0
  for order_line in shopping_cart_product_item_list:
    new_quantity = int(quantity[counter])
    if new_quantity>=1:
      order_line.setQuantity(new_quantity)
    else:
      # Remove it from shopping cart
      shopping_cart.manage_delObjects(order_line.getId())
    counter += 1

# Handle shipping
if field_my_shipping_method not in ['', None]:
  line = getattr(shopping_cart, 'shipping_method', None)
  if line is not None:
    shopping_cart.manage_delObjects(line.getId())
  shipping = portal.restrictedTraverse(field_my_shipping_method)
  # create new shipping method order line
  shopping_cart.newContent(
                 id='shipping_method',
                 portal_type='Sale Order Line',
                 resource_value=shipping,
                 quantity=1)

# Handle payment mode and comment
if field_my_comment is not None:
  shopping_cart.setComment(field_my_comment)

context.WebSection_updateShoppingCartTradeCondition(shopping_cart, field_my_payment_mode, preserve=True)

portal.portal_sessions[container.REQUEST['session_id']].update(shopping_cart=shopping_cart)

if redirect:
  # Hardcode redirection.
  return context.Base_redirect("WebSection_viewShoppingCart", \
                      keep_items={'portal_status_message': translateString("Shopping Cart Updated.")})
