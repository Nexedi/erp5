"""
Public interface to getSnapshot API method - sets headers and returns
output (a pdf file which is generated only once and never changes, even if
file data change).
"""
request = context.REQUEST
request.RESPONSE.setHeader('Content-type', context.getSnapshotContentType())
request.RESPONSE.setHeader('Content-disposition', 'attachment; filename="%s.pdf"' % context.getStandardFilename())
return context.getSnapshotData()
