"""
Extract the client_id from the came_from parameter recevied by the login_once_form.

To be used, for example, to pick a page style when rendering that form.
Once the user is authenticated, the same value can be accessed with:
  from AccessControl import getSecurityManager
  getSecurityManager().getUser().getClientId()
"""
import urlparse
# The came_from for login_once_form is special: it has no scheme, no netloc, a path and a query.
# Verify this so caller knows if they are providing the wrong value.
if not context.ERP5Site_isOAuth2CameFrom(came_from=came_from):
  raise ValueError
result, = [
  value
  for name, value in urlparse.parse_qsl(urlparse.urlsplit(came_from).query)
  if name == 'client_id'
]
return result
