document = state_change['object']
portal = document.getPortalObject()

filename = document.getFilename()
content_type = portal.mimetypes_registry.lookupExtension(filename)

if content_type is None:
  return
content_type = str(content_type)
if content_type != document.getContentType():
  document.setContentType(content_type)
