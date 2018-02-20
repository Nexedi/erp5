"""
  Default logout handler, overwritten to give website specific portal status message.
"""
website = context.getWebSiteValue()
REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
  context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
REQUEST.RESPONSE.expireCookie('__ac_google_hash', path='/')
REQUEST.RESPONSE.expireCookie('__ac_facebook_hash', path='/')
REQUEST.RESPONSE.setHeader('Location', came_from or context.getPermanentURL(context))
REQUEST.RESPONSE.setStatus(303)
# REQUEST.RESPONSE.redirect(came_from or context.getPermanentURL(context));
