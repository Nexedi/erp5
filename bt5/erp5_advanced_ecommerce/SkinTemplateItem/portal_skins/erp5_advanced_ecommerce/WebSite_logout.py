"""
  Default logout handler, overwritten to give website specific portal status message.
"""
website = context.getWebSiteValue()
REQUEST = context.REQUEST
if 'portal_skin' in REQUEST:
  context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
REQUEST.RESPONSE.expireCookie('__ac_facebook_hash', path='/')
REQUEST.RESPONSE.expireCookie('__ac_google_hash', path='/')
REQUEST.RESPONSE.expireCookie('__ac_browser_id_hash', path='/')
REQUEST.RESPONSE.expireCookie('login_come_from_url', path='/')

if not website.SaleOrder_getShoppingCartItemList():
  REQUEST.RESPONSE.expireCookie('session_id', path='/')


msg = context.Base_translateString('You have been logged out. Thank you for using this website.')
return website.Base_redirect(form_id, keep_items = {'portal_status_message' : msg},  **kw)
