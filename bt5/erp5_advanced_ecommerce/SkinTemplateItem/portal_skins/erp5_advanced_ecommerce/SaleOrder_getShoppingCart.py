"""
  Create a new shopping cart if needed. Return
  shopping cart for current customer. Set all local roles
  permissins so that shopping cart can be modified by anonymous.

  TODO:
  - decide whether to keep or remove new_shopping_cart parameter
    (is it really useful to create a new shopping cart here)
"""
request = context.REQUEST
if session_id in [None, '']:
  session_id = request.get('session_id', None)

if session_id in [None, '']:
  # Rely on cookies information
  session_id = request.cookies.get('session_id', None)

if session_id in [None, '']:
  return None

portal_sessions = context.portal_sessions

# take shopping cart for this customer
shopping_cart_id = 'shopping_cart'
session = portal_sessions[session_id]

# some cleanup could be required if the shopping cart
# comes from a previous user with same session
if shopping_cart_id in session.keys():
  shopping_cart = session[shopping_cart_id]
  if shopping_cart.getStartDate() is None:
    shopping_cart.edit(start_date=DateTime())
  #if not shopping_cart.SaleOrder_isShoppingCartConsistent():
  #  portal_sessions.manage_delObjects(session_id)
  #  session = portal_sessions[session_id]

# create shopping cart
if not shopping_cart_id in session.keys():
  shopping_cart = context.sale_order_module.newContent(portal_type="Sale Order",
    temp_object=True,
    id=shopping_cart_id,
    start_date=DateTime(),
    container=portal_sessions)
  # Set usable security for Anonymous
  shopping_cart.manage_role("Anonymous", ["Access contents information",
                                          "Add portal content",
                                          "Delete objects",
                                          "Modify portal content",
                                          "View"])
  context.WebSection_updateShoppingCartTradeCondition(shopping_cart, None)
  user = context.ERP5Site_getAuthenticatedMemberPersonValue()
  if user:
    shopping_cart.setDestinationValue(user)
  shopping_cart.setPriceCurrency(shopping_cart.getSpecialiseValue().getPriceCurrency())
  session[shopping_cart_id] = shopping_cart
## return just a part of session for shopping cart
shopping_cart = session[shopping_cart_id]
return shopping_cart
