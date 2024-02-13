document = state_change['object']
portal = document.getPortalObject()

filename = document.getFilename()
if filename:
  content_type = portal.mimetypes_registry.lookupExtension(filename)
  if content_type is not None:
    document.setContentType(str(content_type))
