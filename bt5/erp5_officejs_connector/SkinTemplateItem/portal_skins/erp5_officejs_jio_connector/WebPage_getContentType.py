web_page = context

portal_type = web_page.getPortalType()
content_type = web_page.getContentType()

if not content_type:
  if (portal_type == "Web Script"):
    content_type = 'application/javascript'
  elif (portal_type == "Web Style"):
    content_type = 'text/css'
  elif (portal_type == "Web Page"):
    content_type = 'text/html'
  elif (portal_type == "Web Manifest"):
    content_type = 'text/cache-manifest'

return content_type
