from base64 import b64encode, b64decode
mime_type = context.getContentType()
if not mime_type:
  mime_type = "application/octet-stream"
return "data:%s;base64,%s" % (mime_type, b64encode(context.getData()))
