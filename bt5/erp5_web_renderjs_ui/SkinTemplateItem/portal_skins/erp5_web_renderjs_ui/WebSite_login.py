import re
REQUEST = context.REQUEST
RESPONSE = REQUEST.RESPONSE
from ZTUtils import make_query

portal = context.getPortalObject()

if (came_from is None):
  #XXX Hardcoded for JS app's url end with '/'
  came_from = "%s/" % context.getPermanentURL(context.getWebSiteValue())

portal.portal_skins.updateSkinCookie()
portal.setupCurrentSkin(REQUEST)

if (portal.portal_membership.isAnonymousUser()):
  RESPONSE.expireCookie('__ac', path='/')

  is_user_account_blocked = REQUEST.get('is_user_account_blocked', False)
  is_user_account_password_expired = REQUEST.get('is_user_account_password_expired', False)
  
  if is_user_account_blocked:
    message = context.Base_translateString('Account is blocked.')
  elif is_user_account_password_expired:
    if (portal.portal_preferences.isPreferredSystemRecoverExpiredPassword()):
      message = context.Base_translateString('Password is expired. You will soon receive an email with details about how you can recover it.')
    else:
      message = context.Base_translateString('Password is expired.')
  else:
    message = context.Base_translateString('Login and/or password is incorrect.')

  url = '%s/login_form?portal_status_message=%s' % (context.absolute_url(), message)
  url = came_from and '%s&%s' % (url, make_query({"came_from": came_from})) or url
  RESPONSE.redirect(url)
else:
  # XXX How to warn user that password will expire?
  # is_user_account_password_expired_expire_date = REQUEST.get('is_user_account_password_expired_expire_date', 0)

  # XXX Hardcoded behaviour for JS app.
  # Expect came_from to be an URL template
  person = portal.portal_membership.getAuthenticatedMember().getUserValue()
  url_parameter = "n.me"
  pattern = '{[&|?]%s}' % url_parameter
  if (person is None or not portal.portal_membership.checkPermission('View', person)):
    came_from = re.sub(pattern, '', came_from)
  else:
    prefix = "&" if "&%s" % url_parameter in came_from else "?"
    came_from = re.sub(pattern, '%s%s' % (prefix, make_query({url_parameter: person.getRelativeUrl()})), came_from)
  # RESPONSE.redirect(came_from or context.getPermanentURL(context));
  RESPONSE.setHeader('Location', came_from or context.getPermanentURL(context))
  RESPONSE.setStatus(303)
