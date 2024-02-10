portal = context.getPortalObject()

cookie_authentication = getattr(portal, 'cookie_authentication', None)
if cookie_authentication is not None \
    and cookie_authentication.getProperty('auth_cookie') == cookie_name \
    and DateTime().millis() >= portal.portal_sessions[
        portal.Base_getAutoLogoutSessionKey(
          username=portal.Base_getUsernameFromAuthenticationCookie(
            cookie_value
          )
        )
      ].get('ac_renew', 0):
  portal.setAuthCookie(resp, cookie_name, cookie_value)
