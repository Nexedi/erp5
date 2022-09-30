from Products.ERP5Type.Cache import CachingMethod

portal = context.getPortalObject()
user = portal.portal_membership.getAuthenticatedMember().getIdOrUserName()

def getModuleItemList(user=None):
  gettext = portal.Localizer.erp5_ui.gettext

  item_list = []
  for module_id in portal.objectIds(spec=('ERP5 Folder',)):
    module = portal.restrictedTraverse(module_id, None)
    if module is not None:
      if portal.portal_membership.checkPermission('View', module):
        item_list.append((gettext(module.getTitleOrId()), module.absolute_url_path()))

  item_list.sort(key=lambda x: x[0])
  return item_list

# XXX The getModuleItemList function should not cache absolute_url_path as it
#     may vary according to where the script is called from. Here we generate
#     the cache key to also vary according to the same condition as the module
#     absolute_url_path results.
request = getattr(context, "REQUEST", None)
if request is not None:
  virtual_root_url = request.physicalPathToURL(portal.getPhysicalPath() + ("",))  # ends with a slash
else:
  virtual_root_url = portal.portal_url()  # does not end with a slash

getModuleItemList = CachingMethod(getModuleItemList,
  id=('ERP5Site_getModuleItemList', portal.Localizer.get_selected_language(), virtual_root_url),
      cache_factory='erp5_ui_short')

return getModuleItemList(user=user)
