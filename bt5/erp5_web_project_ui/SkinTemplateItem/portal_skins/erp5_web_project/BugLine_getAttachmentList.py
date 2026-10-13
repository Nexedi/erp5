"""
  Return the files and images of a bug line as attachments for the thread reader.
"""
result = []
for document in context.contentValues(portal_type=('File', 'Image')):
  result.append({'title': document.getTitle(),
                 'url': document.File_getDownloadUrl(),
                 'content_type': document.getPortalType()})
return result
