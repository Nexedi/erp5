"""
Just returns the data with text/html as content-type
"""
document = context.text_file
context.REQUEST.RESPONSE.setHeader('content-type', 'text/html')
return document.data
