from Products.PythonScripts.standard import Object
inventory_kw = {
  'selection_domain': selection_domain
}

# See Resource_getFutureInventoryList to understand why we
# run catalog queries to retrieve Organisations's uid
# instead of passing category paths to getInventory
if node_category:
  node_uid_list = [
    x.uid for x in portal.portal_catalog(
      portal_type=portal.getPortalNodeTypeList(),
      default_site_uid=portal.portal_categories.resolveCategory(node_category).getUid(),
    )
  ]
  if not node_uid_list:
    return []
  inventory_kw["node_uid"] = node_uid_list
section_uid_list = None
if section_category:
  section_uid_list = [
    x.uid for x in portal.portal_catalog(
      portal_type=portal.getPortalNodeTypeList(),
      default_group_uid=portal.portal_categories.resolveCategory(section_category).getUid(),
    )
  ]
  if not section_uid_list:
    return []
  inventory_kw['section_uid'] = section_uid_list
if quantity_unit:
  inventory_kw['quantity_unit'] = quantity_unit
if metric_type:
  inventory_kw['metric_type'] = metric_type

obj = Object(uid="new_")
obj["node_title"] = ""
obj["section_title"] = ""
obj["variation_text"] = ""
obj["getCurrentInventory"] = context.getCurrentInventory(**inventory_kw)
obj["getAvailableInventory"] = context.getAvailableInventory(**inventory_kw)
obj["inventory"] = context.getFutureInventory(**inventory_kw)

return [obj,]
