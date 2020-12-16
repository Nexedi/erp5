request = context.REQUEST
variation = request.get('variation', None)
image_container = None
if variation:
  image_container = context.getWebSiteValue().restrictedTraverse(variation)
else:
  image_container = context

if image_container is None:
  return []

return image_container.contentValues(portal_type="Embedded File")
