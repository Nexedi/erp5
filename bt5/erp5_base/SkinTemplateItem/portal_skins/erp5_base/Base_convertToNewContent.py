portal = context.getPortalObject()
content_type = context.getContentType()

def splitext(unixpath):
  slashsplit = unixpath.split("/")
  dotsplit = slashsplit[-1].split(".")
  reqlen = 3 if dotsplit[0] == '' else 2
  if len(dotsplit) < reqlen:
    return (unixpath, '')
  return ('/'.join(slashsplit[:-1] + ['.'.join(dotsplit[:-1])]), '.' + dotsplit[-1])

def getTargetFormatItemList(content_type):
  # returns [(title, mimetype), ...]
  if content_type is None:
    return []
  format_list = []
  available_mimetype_list = portal.portal_transforms.getAvailableTargetMimetypeList(content_type)
  mimetype_registry = portal.mimetypes_registry
  for available_mimetype in available_mimetype_list:
    mimetype_info_list = mimetype_registry.lookup(available_mimetype)
    for mimetype_info in mimetype_info_list:
      format_list.append((mimetype_info.name(), available_mimetype))
  return format_list

def getExtension(content_type, default=None):
  for info in portal.mimetypes_registry.lookup(content_type):
    try:
      return info.extensions[0]
    except IndexError:
      pass
  return default

if __list:
  if content_type in ("", None):
    return []
  #return getTargetFormatItemList(content_type)
  #return [("%s (%s)" %(t, mt), mt) for t, mt in getTargetFormatItemList(content_type)]
  return [("%s (%s)" %(t, getExtension(mt, "-")), mt) for t, mt in getTargetFormatItemList(content_type)]

destination_portal_type = portal.portal_contribution_registry.findPortalTypeName(content_type=destination_mimetype)

module_id = portal.getDefaultModuleId(destination_portal_type, default=None, only_visible=True)
extension = getExtension(destination_mimetype, "bin")

data = portal.portal_transforms.convertToData(destination_mimetype, str(context.getData() or ""), context=context, mimetype=content_type)
if data is None:
  raise ValueError("Failed to convert to %r" % destination_mimetype)

document = portal[module_id].newContent(
  portal_type=destination_portal_type,
  title=context.getTitle(),
  short_title=context.getShortTitle(),
  reference=context.getReference(),
  version=version,
  language=context.getLanguage(),
  effective_date=context.getEffectiveDate(),
  filename=splitext(context.getFilename('untitled'))[0] + "." + extension,
  content_type=destination_mimetype,
  data=data,
  category_list=context.getCategoryList(),
  description=context.getDescription(),
)
if REQUEST is None:
  return document
return document.Base_redirect(keep_items={"portal_status_message": context.Base_translateString("Converted successfully")})
