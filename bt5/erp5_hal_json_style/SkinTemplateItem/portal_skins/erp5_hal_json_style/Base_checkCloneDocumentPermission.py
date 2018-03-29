from zExceptions import Unauthorized
try:
  portal = context.getPortalObject()
  return (
    (getattr(context, 'getParentValue', None) is not None) and
    (context.getPortalType() not in portal.getPortalModuleTypeList()) and
    (portal.Base_checkPermission(context.getParentValue().getRelativeUrl(), 'Add portal content')) and
    (context.getPortalType() in context.getParentValue().getVisibleAllowedContentTypeList())
  )
except Unauthorized:
  return False
