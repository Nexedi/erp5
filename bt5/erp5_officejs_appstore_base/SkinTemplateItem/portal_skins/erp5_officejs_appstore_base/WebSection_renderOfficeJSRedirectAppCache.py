if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

web_section = context
modification_date = max(web_section.Base_getWebDocumentDrivenModificationDate(), DateTime().earliestTime()  + (DateTime().hour() /24.0)).rfc822()

if REQUEST.getHeader('If-Modified-Since', '') == modification_date:
  response.setStatus(304)
  return ""

response.setHeader('Content-Type', 'text/cache-manifest')
response.setHeader('Cache-Control', 'max-age=0, public, must-revalidate')

return """CACHE MANIFEST
# %s / %s""" % (context.getLayoutProperty("configuration_latest_version", default="development"), modification_date)
