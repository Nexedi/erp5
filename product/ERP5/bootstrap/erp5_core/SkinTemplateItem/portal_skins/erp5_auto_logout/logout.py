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
portal.acl_users.logout(REQUEST)
return REQUEST.RESPONSE.redirect(REQUEST.URL1 + '/logged_out')
