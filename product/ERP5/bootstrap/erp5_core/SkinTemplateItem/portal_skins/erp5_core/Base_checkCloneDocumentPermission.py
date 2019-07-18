from zExceptions import Unauthorized
try:
  portal = context.getPortalObject()
  if getattr(context, 'getParentValue', None) is None:
    return False
  portal_type = context.getPortalType()
  if portal_type in portal.getPortalModuleTypeList():
    return False
  parent = context.getParentValue()
  return (
    (portal.Base_checkPermission(parent.getRelativeUrl(), 'Add portal content')) and
    (portal_type in parent.getVisibleAllowedContentTypeList())
  )
except Unauthorized:
  return False
