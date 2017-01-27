"""
  Returns a list of acceptable formats for conversion
  in the form of tuples (for listfield in ERP5Form)
"""
from Products.ERP5Type.Cache import CachingMethod

portal = context.getPortalObject()
content_type = context.getContentType()

def getTargetFormatItemList(content_type):
  # returns [(title, extension), ...]
  if content_type is None:
    return []
  format_list = []
  available_mimetype_list = portal.portal_transforms.getAvailableTargetMimetypeList(content_type)
  mimetype_registry = portal.mimetypes_registry
  for available_mimetype in available_mimetype_list:
    mimetype_info_list = mimetype_registry.lookup(available_mimetype)
    for mimetype_info in mimetype_info_list:
      try:
        format_list.append((mimetype_info.name(), mimetype_info.extensions[0]))
      except IndexError:
        pass
  return format_list

getTargetFormatItemList = CachingMethod(getTargetFormatItemList,
                                        id='Base_getTargetFormatItemList',
                                        cache_factory='erp5_ui_long')
return getTargetFormatItemList(content_type)
