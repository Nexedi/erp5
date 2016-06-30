from AccessControl import getSecurityManager
portal = context.getPortalObject()
portal.portal_sessions.manage_delObjects(
  portal.Base_getAutoLogoutSessionKey(
    username=getSecurityManager().getUser().getUserName(),
  )
)
REQUEST = portal.REQUEST
if REQUEST.has_key('portal_skin'):
  portal.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
REQUEST.RESPONSE.expireCookie('d_jwt', path='/')
REQUEST.RESPONSE.expireCookie('n_jwt', path='/')
return REQUEST.RESPONSE.redirect(REQUEST.URL1 + '/logged_out')
