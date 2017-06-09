request = container.REQUEST
mirror_section_title = ''
try:
  return request.other[context.mirror_section_uid]
except KeyError:
  if context.mirror_section_uid:
    brain_list = context.getPortalObject().portal_catalog(uid=context.mirror_section_uid, limit=2)
    if brain_list:
      brain, = brain_list
      mirror_section_title = brain.getObject().getTitle()

request.other[context.mirror_section_uid] = mirror_section_title
return mirror_section_title
