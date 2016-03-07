if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

web_page = context
web_section = REQUEST.get("current_web_section")

if REQUEST.getHeader('If-Modified-Since', '') == web_page.getModificationDate().rfc822():
  response.setStatus(304)
  return ""

portal_type = web_page.getPortalType()
web_content = web_page.getTextContent()

# set headers depending on type of script
if (portal_type == "Web Script"):
  response.setHeader('Content-Type', 'application/javascript')

elif (portal_type == "Web Style"):
  response.setHeader('Content-Type', 'text/css')

elif (portal_type == "Web Manifest"):
  response.setHeader('Content-Type', 'text/cache-manifest')

else:
  if (mapping_dict is not None):
    web_content = web_page.TextDocument_substituteTextContent(web_page, web_content, mapping_dict=mapping_dict)

  content_security_policy = "default-src 'self' data: blob:"
  if (web_section):
    content_security_policy = web_section.getLayoutProperty("configuration_content_security_policy", default=content_security_policy)

  # Do not allow to put inside an iframe
  response.setHeader("X-Frame-Options", "SAMEORIGIN")
  response.setHeader("X-Content-Type-Options", "nosniff")

  # Only fetch code (html, js, css, image) and data from this ERP5, to prevent any data leak as the web site do not control the gadget's code
  response.setHeader("Content-Security-Policy", content_security_policy)

  response.setHeader('Content-Type', 'text/html')

return web_content
