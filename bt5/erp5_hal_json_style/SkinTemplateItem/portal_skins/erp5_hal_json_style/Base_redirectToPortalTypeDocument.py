portal = context.getPortalObject()
type_info = portal.portal_types.getTypeInfo(context)
if type_info is not None and type_info.Base_getSourceVisibility():
  return type_info.Base_redirect("view")
