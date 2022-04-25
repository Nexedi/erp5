from six.moves.urllib.parse import urlparse

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

REQUEST = portal.REQUEST
parse_dict = urlparse(REQUEST.other.get('ACTUAL_URL'))
same_site = portal.ERP5Site_getAuthCookieSameSite(scheme=parse_dict.scheme,
                                                  hostname=parse_dict.hostname,
                                                  port=parse_dict.port,
                                                  path=parse_dict.path,
                                                  user_agent=REQUEST.environ.get('HTTP_USER_AGENT'))
if same_site not in ('None', 'Lax', 'Strict'):
  # Do not use the SameSite attribute
  same_site = None

resp.setCookie(
  name=cookie_name,
  value=cookie_value,
  path='/',
  secure=REQUEST.get('SERVER_URL', '').startswith('https:'),
  http_only=True,
  same_site=same_site,
  **kw
)
