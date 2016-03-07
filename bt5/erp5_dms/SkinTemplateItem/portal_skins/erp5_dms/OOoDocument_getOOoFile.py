"""
Public interface to getBaseData API method - invokes index_html
to return the file in the base-data format.
"""
request = context.REQUEST
response = request.RESPONSE
response.setHeader('Content-disposition', 'attachment; filename="%s"' % context.getStandardFilename())
return context.index_html(request, response, format='base-data')
