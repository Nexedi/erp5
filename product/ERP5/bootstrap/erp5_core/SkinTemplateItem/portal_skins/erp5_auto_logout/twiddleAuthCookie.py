portal = context.getPortalObject()
if DateTime().millis() >= portal.portal_sessions[portal.Base_getAutoLogoutSessionKey()].get('ac_renew', 0):
  portal.setAuthCookie(resp, cookie_name, cookie_value)
