"""
Processes requests for conversion of and Image to a desired format.
Requires format and desired filename (adds extension if missing).
Sets headers and uses native Zope method to produce output.
"""

request = context.REQUEST
fname = request.get('filename')
format = request.get('format')

if fname is None or format is None:
  return
if not fname.endswith('.' + format):
  fname += '.' + format

request.RESPONSE.setHeader('Content-type', 'application/' + format)
request.RESPONSE.setHeader('Content-disposition', 'attachment; filename="%s"' % fname)
return context.index_html(request, request.RESPONSE, **kw)
