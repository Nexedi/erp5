"""
  Default logout handler, overwritten to give website specific portal status message.
"""
from AccessControl import getSecurityManager
portal = context.getPortalObject()
user = getSecurityManager().getUser()
username = user.getId()
if username is not None:
  portal.portal_sessions.manage_delObjects(
    portal.Base_getAutoLogoutSessionKey(
      username=username,
    )
  )
REQUEST = portal.REQUEST
if 'portal_skin' in REQUEST:
  portal.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')

if getattr(portal.portal_skins, "erp5_oauth_google_login", None):
  REQUEST.RESPONSE.expireCookie('__ac_google_hash', path='/')

if getattr(portal.portal_skins, "erp5_oauth_facebook_login", None):
  REQUEST.RESPONSE.expireCookie('__ac_facebook_hash', path='/')

if getattr(portal.portal_skins, "erp5_openid_connect_client", None):
  REQUEST.RESPONSE.expireCookie('__ac_openidconnect_hash', path='/')

# PAS logout, if user is from a PAS user folder (which is the acquisition parent of the user)
getattr(
  user,
  'resetCredentials',
  lambda **kw: None,
)(
  request=REQUEST,
  response=REQUEST.RESPONSE,
)
REQUEST.RESPONSE.setHeader('Location', came_from or context.getPermanentURL(context))
REQUEST.RESPONSE.setStatus(303)
# REQUEST.RESPONSE.redirect(came_from or context.getPermanentURL(context));
