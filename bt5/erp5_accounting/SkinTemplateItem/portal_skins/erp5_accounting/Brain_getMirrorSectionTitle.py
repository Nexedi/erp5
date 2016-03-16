request = container.REQUEST
mirror_section_title = ''
try:
  return request.other[context.mirror_section_uid]
except KeyError:
  if context.mirror_section_uid:
    mirror_section = context.getPortalObject().portal_catalog.getobject(context.mirror_section_uid)
    if mirror_section is not None:
      mirror_section_title = mirror_section.getTitle()
  
request.other[context.mirror_section_uid] = mirror_section_title
return mirror_section_title
