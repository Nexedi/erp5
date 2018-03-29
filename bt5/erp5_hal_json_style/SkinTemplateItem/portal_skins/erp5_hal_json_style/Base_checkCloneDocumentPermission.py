from zExceptions import Unauthorized
try:
  portal = context.getPortalObject()
  object = context
  return (getattr(object, 'getParentValue', None) is not None) and (object.getPortalType() not in portal.getPortalModuleTypeList()) and (portal.Base_checkPermission(object.getParentValue().getRelativeUrl(), 'Add portal content')) and (object.getPortalType() in object.getParentValue().getVisibleAllowedContentTypeList())
except Unauthorized:
  return False
