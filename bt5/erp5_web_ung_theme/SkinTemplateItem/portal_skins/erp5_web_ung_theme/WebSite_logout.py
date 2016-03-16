REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
   context.portal_skins.clearSkinCookie()

# XXX get cookie name from key authentication plugin
REQUEST.RESPONSE.expireCookie('__ac', path="/")
REQUEST.RESPONSE.expireCookie('__key', path="/")

return context.Base_redirect(context.absolute_url())
