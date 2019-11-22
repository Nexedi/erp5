if REQUEST is None:
  REQUEST = context.REQUEST
if response is None:
  response = REQUEST.RESPONSE

file_document = context
file_content = file_document.getData()

# The vanilla HTML is wanted
response.setBase(None)

# Allow any external app to download the source code
response.setHeader("Access-Control-Allow-Origin", "*")

if REQUEST.getHeader('If-Modified-Since', '') == file_document.getModificationDate().rfc822():
  response.setStatus(304)
  return ""

#file_content_type = file.getContentType()
#if file_content_type is None:
#  file_content_type = 'application/octet-stream'

response.setHeader('Content-Type', (file_document.getContentType() or 'application/octet-stream'))

return file_content
