"""Get translation id dict based on parent portal type"""
parent_portal_type = context.getParentValue().getPortalType().replace(' ','')
method = getattr(context, "%s_getLinkIdTranslationDict" % parent_portal_type, None)

if not method:
  return {}

return method()
