document = context.text_file
context.REQUEST.RESPONSE.setHeader('content-type', 'text/plain')
context.REQUEST.RESPONSE.setHeader('content-disposition', 'attachment; filename="%s"' % filename)
return document.data
