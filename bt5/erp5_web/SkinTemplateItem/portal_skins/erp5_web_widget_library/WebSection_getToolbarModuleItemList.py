from Products.ERP5Type.Cache import CachingMethod

# by default we use following modules in toolbar.
if module_id_list is None:
  module_id_list = context.WebSection_getDefaultToolbarModuleItemList()

portal = context.getPortalObject()
user = portal.portal_membership.getAuthenticatedMember().getIdOrUserName()
web_site_id = getattr(context, 'getWebSiteValue', None) is not None and \
    context.getWebSiteValue().getId()

def getModuleItemList(user=None):
  gettext = portal.Localizer.erp5_ui.gettext

  item_list = []
  for module_id in module_id_list:
    module = portal.restrictedTraverse(module_id, None)
    if module is not None:
      if portal.portal_membership.checkPermission('View', module):
        item_list.append((gettext(module.getTitleOrId()), module.absolute_url_path()))

  item_list.sort(key=lambda x: x[0])
  return item_list

getModuleItemList = CachingMethod(getModuleItemList,
  id=('WebSection_getToolbarModuleItemList', portal.Localizer.get_selected_language(), portal.portal_url(), web_site_id),
      cache_factory='erp5_ui_short')

return getModuleItemList(user=user)
