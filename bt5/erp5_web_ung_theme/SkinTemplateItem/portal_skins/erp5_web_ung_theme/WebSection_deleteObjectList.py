portal_type_list = ["Web Page", "Web Table", "Web Illustration", "Email Thread"]

portal = context.getPortalObject()
uid_list = context.REQUEST.get("uids")

if uid_list is not None:
  for catalog_object in portal.portal_catalog(portal_type=portal_type_list, 
                                      uid=uid_list):
    object = context.restrictedTraverse(catalog_object.getPath())
    if object.getValidationState() == "deleted":
      parent_folder = object.getParent()
      parent_folder.deleteContent(object.getId())
    else:
      object.delete()

return context.ERP5Site_redirect(context.REQUEST.get("HTTP_REFERER"))
