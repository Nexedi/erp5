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

REQUEST_DICT = getattr(portal, 'REQUEST', {})

same_site = portal.ERP5Site_getSameSite(host=REQUEST_DICT.get('HTTP_HOST', None))
if same_site not in ('None', 'Lax', 'Strict'):
  # Do not use the SameSite attribute
  same_site = None

resp.setCookie(
  name=cookie_name,
  value=cookie_value,
  path='/',
  secure=REQUEST_DICT.get('SERVER_URL', '').startswith('https:'),
  http_only=True,
  same_site=same_site,
  **kw
)
