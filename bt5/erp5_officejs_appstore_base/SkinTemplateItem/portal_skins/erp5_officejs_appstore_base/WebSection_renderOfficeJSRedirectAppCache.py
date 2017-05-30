if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

web_section = context

if REQUEST.getHeader('If-Modified-Since', '') == web_section.getModificationDate().rfc822():
  response.setStatus(304)
  return ""

response.setHeader('Content-Type', 'text/cache-manifest')
response.setHeader('Cache-Control', 'max-age=0, public, must-revalidate')

return """CACHE MANIFEST
# %s""" % context.getLayoutProperty("configuration_latest_version", default="development")
