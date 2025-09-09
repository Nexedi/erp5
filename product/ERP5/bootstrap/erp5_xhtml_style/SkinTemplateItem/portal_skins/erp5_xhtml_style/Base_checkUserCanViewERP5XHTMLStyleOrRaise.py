# Override this script to control user access to ERP5 XHTML-style rendering.
from zExceptions import Redirect

portal = context.getPortalObject()
if portal.portal_membership.isAnonymousUser():
  web_site_value = context.getWebSiteValue()
  if web_site_value is None:
    if context.getRelativeUrl() != portal.getRelativeUrl():
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
