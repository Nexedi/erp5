# Override this script to control user access to ERP5 XHTML-style rendering.
from zExceptions import Redirect

portal = context.getPortalObject()
if portal.portal_membership.isAnonymousUser():
  # Forbid the usage of the ignore_layout parameter for anonymous user
  # This prevents web bots to crawl xhtml style, as it leads to a lot of urls
  web_site_value = context.getWebSiteValue()
  if web_site_value is not None:
    if portal.REQUEST.form.get('ignore_layout', None):
      # Use the 303 status code, to ensure changing the HTTP method to a GET
      portal.REQUEST.RESPONSE.setStatus(303, lock=True)
      raise Redirect(web_site_value.absolute_url())
