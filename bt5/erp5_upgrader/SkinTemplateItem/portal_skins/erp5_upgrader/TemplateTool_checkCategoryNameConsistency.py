# This script is called as a "script constraint"
# It will replace an old base category name by a new name, and update all
# related objects.
# To get the list of changes, we use the same idea as in TemplateTool_checkBusinessTemplateInstallation :
# we get a list of tuples containing the old names and new names from a Script (Python),
# which should be overriden in the custom sites' upgraders.
# Because this script is called during the post-upgrade phase, we are
# looking for the category by its new name.

if activate_kw is None:
  activate_kw = {}

portal = context.getPortalObject()

error_list = []

upgrade_list = context.Base_getUpgradeCategoryNameList()

if not upgrade_list:
  return []

for old_category_name, new_category_name in upgrade_list:

  sensitive_portal_type_list = []
  new_base_category_id = new_category_name.split('/')[0]
  
  # We gather portal types having the new category defined as a property
  for portal_type in portal.portal_types.listTypeInfo():
    if new_base_category_id in portal_type.getInstancePropertyAndBaseCategoryList():
      sensitive_portal_type_list.append(portal_type.getId())

  # if sensitive_portal_type_list is empty, we don't want to check all objects
  if fixit and sensitive_portal_type_list:
    context.portal_catalog.searchAndActivate('Base_updateRelatedCategory',
      activate_kw=activate_kw,
      portal_type=sensitive_portal_type_list,
      method_kw={'fixit': fixit,
                  'old_category_name': old_category_name,
                  'new_category_name': new_category_name,}
    )

  for portal_type in sensitive_portal_type_list:
    error_list.append('Portal Type %s still contains the category %s' % (portal_type, old_category_name))

return error_list
