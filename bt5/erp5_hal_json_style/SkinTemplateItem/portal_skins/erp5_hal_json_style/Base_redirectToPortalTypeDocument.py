portal = context.getPortalObject()
type_info = portal.portal_types.getTypeInfo(context)
if type_info is not None and type_info.Base_getSourceVisibility():
  translate = context.Base_translateString
  return type_info.Base_redirect(
    keep_items={
      "portal_status_message": "%s: %s" % (
        translate("Portal Type"),
        translate(type_info.getTitle()))
    })
