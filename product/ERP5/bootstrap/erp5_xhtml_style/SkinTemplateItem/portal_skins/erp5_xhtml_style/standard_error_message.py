"""
  Tries to render the error with classic UI including all toolbars.
  If the user is unauthorized to show it from this context, then
  it tries to render the error from the web site root. If no web site
  root is defined then it renders the error from portal.
"""
from zExceptions import Unauthorized
request = container.REQUEST

# set response header for ERP5JS display of errors
request.response.setHeader('X-ERP5-Error-Type', kw.get('error_type'))
request.response.setHeader('X-ERP5-Error-Value', kw.get('error_value'))
error_log_url = kw.get('error_log_url')
if error_log_url:
  request.response.setHeader('X-ERP5-Error-Log-URL', error_log_url)

try:
  return context.standard_error_message_template(*args, **kw)
except Unauthorized:
  pass
try:
  # Note: - user can be unauthorized to getWebSiteValue() from this context
  #       - "web_site_value" comes from erp5.Document.WebSite.WEBSITE_KEY (unauthorized to import)
  web_site_split_path = request.get("web_site_value")
  if web_site_split_path:
    web_site_value = context.getPortalObject().restrictedTraverse(web_site_split_path, None)
    if web_site_value is not None:
      return web_site_value.standard_error_message_template(*args, **kw)
except Unauthorized:
  pass
return context.getPortalObject().standard_error_message_template(*args, **kw)
