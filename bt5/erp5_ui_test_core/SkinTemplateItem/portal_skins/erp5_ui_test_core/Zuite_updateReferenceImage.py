from StringIO import StringIO
portal = context.getPortalObject()

image_file = StringIO(image_data.replace('data:image/png;base64,', '').decode('base64'))

image_path = image_path.split('/')
existing = portal.restrictedTraverse(image_path, None)

if existing is None:
  container = portal.restrictedTraverse(image_path[:-1])
  container.manage_addProduct['OFSP'].manage_addImage(
    image_path[-1],
    image_file,
    '')

else:
  existing.manage_upload(image_file)

return "reference image at {} updated".format('/'.join(image_path))
