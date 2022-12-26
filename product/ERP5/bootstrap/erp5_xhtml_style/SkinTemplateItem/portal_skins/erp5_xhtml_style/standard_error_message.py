"""
  Tries to render the error with classic UI including all toolbars.
  If the user is unauthorized to show it from this context, then
  it tries to render the error from the web site root. If no web site
  root is defined then it renders the error from portal.
"""
from zExceptions import Unauthorized

# Adjust exception context for Zope 4.
context = container.REQUEST.get('PARENTS', [context])[0]

try:
  return context.standard_error_message_template(*args, **kw)
except Unauthorized:
  pass
try:
  # Note: - user can be unauthorized to getWebSiteValue() from this context
  #       - "web_site_value" comes from erp5.Document.WebSite.WEBSITE_KEY (unauthorized to import)
  web_site_split_path = context.REQUEST.get("web_site_value")
  if web_site_split_path:
    web_site_value = context.getPortalObject().restrictedTraverse(web_site_split_path, None)
    if web_site_value is not None:
      return web_site_value.standard_error_message_template(*args, **kw)
except Unauthorized:
  pass
return context.getPortalObject().standard_error_message_template(*args, **kw)
