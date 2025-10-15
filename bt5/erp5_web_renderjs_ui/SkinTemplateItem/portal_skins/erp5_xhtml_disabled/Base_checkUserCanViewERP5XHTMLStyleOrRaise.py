from zExceptions import Forbidden, Redirect
from AccessControl import getSecurityManager

portal = context.getPortalObject()
preference_tool = portal.portal_preferences
if preference_tool.isPreferredHtmlStyleDisabled():
  u = getSecurityManager().getUser()
  user_id = u.getId()
  allowed_user_id_list = preference_tool.getPreferredHtmlStyleAllowedUserIdList()
  #user is not in allowed list or anonymous access when allowed list is empty
  if (user_id and user_id not in allowed_user_id_list) or (not user_id and not allowed_user_id_list):
    raise Forbidden('xhtml_style is disabled. Please use ERP5JS')

elif portal.portal_membership.isAnonymousUser():
  web_site_value = context.getWebSiteValue()
  if web_site_value is None:
    if context.getRelativeUrl() not in [portal.getRelativeUrl(), portal.portal_password.getRelativeUrl()]:
      # Forbid rendering a document in xhtml style
      # and force users to be authenticated
      portal.REQUEST.RESPONSE.setStatus(303, lock=True)
      raise Redirect(portal.absolute_url())
  else:
    # Forbid the usage of the ignore_layout parameter for anonymous user
    # This prevents web bots to crawl xhtml style, as it leads to a lot of urls
    if portal.REQUEST.form.get('ignore_layout', None):
      # Use the 303 status code, to ensure changing the HTTP method to a GET
      portal.REQUEST.RESPONSE.setStatus(303, lock=True)
      raise Redirect(web_site_value.absolute_url())
