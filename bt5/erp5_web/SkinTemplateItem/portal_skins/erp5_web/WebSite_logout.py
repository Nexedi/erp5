"""
  Default logout handler, overwritten to give website specific portal status message.
"""
website = context.getWebSiteValue()
REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
  context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
msg = context.Base_translateString('You have been logged out. Thank you for using this website.')
return website.Base_redirect(form_id, keep_items = {'portal_status_message' : msg},  **kw)
