"""Copy the credential update image to the related entity
Proxy
Manager -- allow to update all image property"""

if REQUEST is not None:
  raise ValueError("This script can not be call from url")

def getAccessor(prop):
  return "".join([x.capitalize() for x in prop.split('_')])

def copyValue(source_document, source_accessor,
              destination_document, destination_accessor):
  getter = getattr(source_document, 'get%s' % source_accessor)
  value = getter()
  setter = getattr(destination_document, 'set%s' % destination_accessor)
  setter(value)

def copyDocument(source_document, destination_document, mapping):
  for source_property, destination_property in mapping:
    source_accessor, destination_accessor = getAccessor(source_property), getAccessor(destination_property)
    copyValue(source_document, source_accessor,
              destination_document, destination_accessor)

new_default_image = context.getDefaultImageValue()
if new_default_image is not None:
  updated_item = context.getDestinationDecisionValue()
  default_image = updated_item.getDefaultImageValue()
  if default_image is None:
    default_image = updated_item.newContent(portal_type="Embedded File",id="default_image")

  image_mapping = (
    # (credential image, item image)
    ('source_reference', 'source_reference'),
    ('content_type', 'content_type'),
    ('content_md5', 'content_md5'),
    ('data', 'data'),
    ('base_data', 'base_data'),
    ('base_content_type', 'base_content_type'),
    )


  copyDocument(new_default_image,default_image, image_mapping)
