# request = container.REQUEST
# if request.form.get('view', None) == 'jio_view':
portal_type = context.getPortalType()
filename = context.getFilename()
if portal_type == 'Spreadsheet' and not filename.endswith('.xlsy'):
  # return context.convert(format='xlsy')
  metadata, data = context.convert(format='xlsy')
  context.setData(data)
  context.setContentType(metadata)
  context.setFilename('.'.join(filename.split('.')[:-1]) + '.xlsy')
else:
  data = context.getData()
# return context.Document_viewAsJio()
return data
