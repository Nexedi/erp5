"""
  Add resource to current (or to be created shopping cart).
"""
from DateTime import DateTime

request = context.REQUEST
expire_timeout_days = 90
session_id = request.get('session_id', None)
portal_sessions = context.portal_sessions

if session_id is None:
  ## first call so generate session_id and send back via cookie
  now = DateTime()
  session_id = context.Base_generateSessionID(max_long=20)
  request.RESPONSE.setCookie('session_id', session_id, expires=(now +expire_timeout_days).fCommon(), path='/')

if action=='reset':
  ## reset cart
  portal_sessions.manage_delObjects(session_id)
else:
  ## take shopping cart for this customer
  shopping_cart_id = 'shopping_cart'
  session = portal_sessions[session_id]
  if not shopping_cart_id in session.keys():
    web_site = context.getWebSiteValue()
    shopping_cart = context.getPortalObject().newContent(temp_object=True, portal_type='Order', id=shopping_cart_id)
    shopping_cart.setPriceCurrency(web_site.WebSite_getShoppingCartDefaultCurrency().getRelativeUrl())
    session[shopping_cart_id] = shopping_cart

  ## return just a part of session for shopping cart
  shopping_cart = session[shopping_cart_id]
  return shopping_cart
