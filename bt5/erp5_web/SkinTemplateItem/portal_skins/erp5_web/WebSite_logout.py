"""
  Default logout handler, overwritten to give website specific portal status message.
"""
from AccessControl import getSecurityManager
portal = context.getPortalObject()
REQUEST = portal.REQUEST
if not portal.ERP5Site_isCookieAuthenticationTrustable(REQUEST):
  # Prevent an attacker from logging-out users by tricking them into opening this script's URL (DoS).
  return
if REQUEST.has_key('portal_skin'):
  portal.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
# PAS logout, if user is from a PAS user folder (which is the acquisition parent of the user)
getattr(
  getSecurityManager().getUser(),
  'resetCredentials',
  lambda **kw: None,
)(
  request=REQUEST,
  response=REQUEST.RESPONSE,
)
context.getWebSiteValue().Base_redirect(
  form_id,
  keep_items={
    'portal_status_message': context.Base_translateString('You have been logged out. Thank you for using this website.'),
  },
  **kw
)
