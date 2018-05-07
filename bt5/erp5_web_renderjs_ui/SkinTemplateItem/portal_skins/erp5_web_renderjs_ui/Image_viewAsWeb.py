if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

# The vanilla HTML is wanted
response.setBase(None)

image = context
if REQUEST.getHeader('If-Modified-Since', '') == image.getModificationDate().rfc822():
  response.setStatus(304)
  return ""
web_content = image.getData()

response.setHeader('Content-Type', image.getContentType())

return web_content
