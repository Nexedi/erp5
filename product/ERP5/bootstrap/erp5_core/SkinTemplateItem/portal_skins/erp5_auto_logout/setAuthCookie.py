portal = context.getPortalObject()
kw = {}
expire_interval = portal.portal_preferences.getPreferredMaxUserInactivityDuration()
if expire_interval in ('', None):
  ac_renew = float('inf')
else:
  expire_interval /= 86400. # seconds -> days
  now = DateTime()
  kw['expires'] = (now + expire_interval).toZone('GMT').rfc822()
  ac_renew = (now + expire_interval / 2).millis()
portal.portal_sessions[
  portal.Base_getAutoLogoutSessionKey(
    username=portal.Base_getUsernameFromAuthenticationCookie(
      cookie_value,
    )
  )
]['ac_renew'] = ac_renew

same_site_cookie = 'Lax'
current_web_section = getattr(portal, 'REQUEST', {}).get('current_web_section', None)
if current_web_section is not None:
  same_site_cookie = current_web_section.getLayoutProperty("same_site_cookie", default=same_site_cookie)
if same_site_cookie not in ('None', 'Lax', 'Strict'):
  # If there is a typo, go back to default value, or it will break erp5 usage
  same_site_cookie = 'Lax'

resp.setCookie(
  name=cookie_name,
  value=cookie_value,
  path='/',
  secure=getattr(portal, 'REQUEST', {}).get('SERVER_URL', '').startswith('https:'),
  http_only=True,
  same_site=same_site_cookie,
  **kw
)
