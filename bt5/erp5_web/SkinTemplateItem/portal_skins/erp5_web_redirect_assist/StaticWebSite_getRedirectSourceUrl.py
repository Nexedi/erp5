"""
================================================================================
Redirect to domain specified as layout property on website
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------

INDEX = "index.html"
REQUEST = context.REQUEST
query_string = REQUEST["QUERY_STRING"]
redirect_domain = context.getProperty("redirect_domain")
redirect_url = redirect_domain
status_code = 301

if not redirect_url.startswith("http"):
  raise ValueError("Redirect URL must start with http/https.")
if context.getProperty("use_moved_temporarily"):
  status_code = 302

try:
  source_path = REQUEST.other["source_path"]
  redirect_url = "/".join([redirect_url, source_path])
except(KeyError):
  redirect_url = redirect_url + "/"

if query_string:
  redirect_url = '?'.join([redirect_url, query_string])
if redirect_url.find(INDEX) > -1 and not redirect_url.endswith(INDEX):
  redirect_url = redirect_url.replace(INDEX, '')
if redirect_url.find(INDEX) > -1 and REQUEST.other['actual_url'].find(INDEX) == -1:
  redirect_url = redirect_url.replace(INDEX, '')

return context.Base_redirect(redirect_url, status_code=status_code)
