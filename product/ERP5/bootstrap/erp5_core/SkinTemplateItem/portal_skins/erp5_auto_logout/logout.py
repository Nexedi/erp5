portal = context.getPortalObject()
portal.portal_sessions.manage_delObjects(portal.Base_getAutoLogoutSessionKey())
REQUEST = portal.REQUEST
if REQUEST.has_key('portal_skin'):
  portal.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
return REQUEST.RESPONSE.redirect(REQUEST.URL1 + '/logged_out')
