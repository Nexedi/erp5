import re
REQUEST = context.REQUEST
RESPONSE = REQUEST.RESPONSE
from ZTUtils import make_query

portal = context.getPortalObject()

if (came_from is None):
  came_from = context.getPermanentURL(context)

portal.portal_skins.updateSkinCookie()
portal.setupCurrentSkin(REQUEST)

if (portal.portal_membership.isAnonymousUser()):
  RESPONSE.expireCookie('__ac', path='/')
  url = '%s/login_form?portal_status_message=%s' % (context.absolute_url(), context.Base_translateString('Login and/or password is incorrect.'))
  url = came_from and '%s&came_from=%s' % (url, came_from) or url;
  RESPONSE.redirect(url)
else:
  # XXX Hardcoded behaviour for JS app.
  # Expect came_from to be an URL template
  person = portal.ERP5Site_getAuthenticatedMemberPersonValue()
  url_parameter = "n.me"
  pattern = '{[&|?]%s}' % url_parameter
  if (person is None):
    came_from = re.sub(pattern, '', came_from)
  else:
    prefix = "&" if "&%s" % url_parameter in came_from else "?"
    came_from = re.sub(pattern, '%s%s' % (prefix, make_query({url_parameter: person.getRelativeUrl()})), came_from)
  # RESPONSE.redirect(came_from or context.getPermanentURL(context));
  RESPONSE.setHeader('Location', came_from or context.getPermanentURL(context))
  RESPONSE.setStatus(303)
