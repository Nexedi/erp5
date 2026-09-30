document = state_change['object']
portal = document.getPortalObject()

filename = document.getFilename()
content_type = None
if filename:
  content_type_from_filename = portal.mimetypes_registry.lookupExtension(filename)
  if content_type_from_filename:
    content_type = str(content_type_from_filename)

document.setContentType(content_type)
