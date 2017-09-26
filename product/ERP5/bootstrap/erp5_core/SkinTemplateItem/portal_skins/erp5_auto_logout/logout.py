from AccessControl import getSecurityManager
portal = context.getPortalObject()
username = getSecurityManager().getUser().getId()
if username is not None:
  portal.portal_sessions.manage_delObjects(
    portal.Base_getAutoLogoutSessionKey(
      username=username,
    )
  )
REQUEST = portal.REQUEST
if REQUEST.has_key('portal_skin'):
  portal.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')

if getattr(portal.portal_skins, "erp5_oauth_google_login", None):
  REQUEST.RESPONSE.expireCookie('__ac_google_hash', path='/')

if getattr(portal.portal_skins, "erp5_oauth_facebook_login", None):
  REQUEST.RESPONSE.expireCookie('__ac_facebook_hash', path='/')

return REQUEST.RESPONSE.redirect(REQUEST.URL1 + '/logged_out')
