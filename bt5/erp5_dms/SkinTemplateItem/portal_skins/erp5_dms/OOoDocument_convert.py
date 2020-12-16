# this script has an `format` argument
# pylint: disable=redefined-builtin
"""
Convert OOoDocument (context) to a desired format and return as a binary `filename` file.
Requires format and desired filename (adds extension if missing).
Sets headers and uses native Zope method to produce output.
"""

request = context.REQUEST

if not filename.endswith('.' + format):
  filename += '.' + format

request.RESPONSE.setHeader('Content-Type', 'application/' + format)
request.RESPONSE.setHeader('Content-Disposition', 'attachment; filename="%s"' % filename)

return context.index_html(request, request.RESPONSE)
