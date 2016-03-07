document = context.text_file
context.REQUEST.RESPONSE.setHeader('content-type', 'text/plain')
return document.data
