REQUEST = context.REQUEST
RESPONSE = REQUEST.RESPONSE

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
  url = came_from and '%s&came_from=%s' % (url, came_from) or url
  RESPONSE.redirect(url)
else:
  # XXX How to warn user that password will expire?
  # is_user_account_password_expired_expire_date = REQUEST.get('is_user_account_password_expired_expire_date', 0)

  came_from = context.WebSection_renderCameFromURITemplate(came_from)
  # RESPONSE.redirect(came_from or context.getPermanentURL(context));
  RESPONSE.setHeader('Location', came_from or context.getPermanentURL(context))
  RESPONSE.setStatus(303)
