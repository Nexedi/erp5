"""
  Returns a list of acceptable formats for conversion
  in the form of tuples (for listfield in ERP5Form)
"""
from Products.ERP5Type.Cache import CachingMethod

def contentTypeMatch(content_type, glob):
  if '*' == glob[-1]:
    # 'image/png' must match 'image/*'
    index = glob.index('*')
    return content_type[:index] == glob[:index]
  else:
    return content_type == glob

portal = context.getPortalObject()
content_type = context.getContentType()

def getTargetFormatItemList(content_type):
  # without content type no wayto determine target format
  if content_type is None:
    return []
  format_list = []
  output_content_type_list = []
  for obj in portal.portal_transforms.objectValues():
    for input in obj.inputs:
      if contentTypeMatch(content_type, input) and \
        obj.output not in output_content_type_list and\
        obj.output!=content_type:
        output_content_type_list.append(obj.output)

  for output_content_type in output_content_type_list:
    mimetypes_registry_extension_list = portal.mimetypes_registry.lookup(output_content_type)
    for mimetypes_registry_extension in mimetypes_registry_extension_list:
      title = mimetypes_registry_extension.name()
      try:
        format = mimetypes_registry_extension.extensions[0]
      except IndexError:
        format = None
      if format is not None and format not in format_list:
        format_list.append((title, format,))
  return format_list

getTargetFormatItemList = CachingMethod(getTargetFormatItemList,
                                        id='Base_getTargetFormatItemList',
                                        cache_factory='erp5_ui_long')
return getTargetFormatItemList(content_type)
