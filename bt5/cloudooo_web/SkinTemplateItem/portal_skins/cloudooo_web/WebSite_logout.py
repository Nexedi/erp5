"""
  From default logout handler, overwritten to give website specific portal status message.
  Add message parameter to allow personal message. Add expirtation on __key cookie.
"""
#XXX-To be commited in trunk ?

website = context.getWebSiteValue()
REQUEST = context.REQUEST
if 'portal_skin' in REQUEST:
   context.portal_skins.clearSkinCookie()

#XXX get cookie name from key authentication plugin
REQUEST.RESPONSE.expireCookie('__ac', path='/')
REQUEST.RESPONSE.expireCookie('__key', path='/')

msg = context.Base_translateString(message)
return website.Base_redirect(form_id, keep_items = {'portal_status_message' : msg},  **kw)
