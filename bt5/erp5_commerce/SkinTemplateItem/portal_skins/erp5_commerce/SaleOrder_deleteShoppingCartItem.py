"""
  Delete a shopping cart item.
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString
shopping_cart = context.SaleOrder_getShoppingCart()

if field_my_order_line_id is not None:
  shopping_cart.manage_delObjects(field_my_order_line_id)
  portal_status_message = "Successfully removed from shopping cart."
else:
  portal_status_message = "Please select an item."

portal.portal_sessions[container.REQUEST['session_id']].update(shopping_cart=shopping_cart)
context.Base_redirect(form_id, \
                      keep_items={'portal_status_message': translateString(portal_status_message, mapping={})})
