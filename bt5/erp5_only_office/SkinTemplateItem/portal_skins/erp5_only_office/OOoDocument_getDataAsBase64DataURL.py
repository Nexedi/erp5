import base64
base64_data = base64.b64encode(bytes(context.getData())).decode().replace('\n', '')

return 'data:%s;base64,%s' % (
  context.getContentType(),
  base64_data)
