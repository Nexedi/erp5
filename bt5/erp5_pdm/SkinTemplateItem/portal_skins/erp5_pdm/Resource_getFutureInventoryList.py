from Products.PythonScripts.standard import Object
portal = context.getPortalObject()

inventory_list_kw = {
    'selection_domain': selection_domain,
    'group_by_section': False,
    'group_by_node': True,
    'group_by_variation': True,
    'resource_uid': context.getUid(),
}

# By passing node_uid and section_uid instead of node_category and
# section_category, we bypass 2 joins on category tables, and can
# directly use a good index:
# `resource_section_node_uid` (`resource_uid`,`section_uid`,`node_uid`,`simulation_state`)
# So it's better to run 2 catalog queries to retrieve the uid
# of the Organisations beforehand instead of confusing the catalog
# and making it go through huge joins (where no index can be used)
if node_category:
  node_uid_list = [
    x.uid for x in portal.portal_catalog(
      portal_type=portal.getPortalNodeTypeList(),
      default_site_uid=portal.portal_categories.resolveCategory(node_category).getUid(),
    )
  ]
  if not node_uid_list:
    return []
  inventory_list_kw["node_uid"] = node_uid_list
if section_category:
  section_uid_list = [
    x.uid for x in portal.portal_catalog(
      portal_type=portal.getPortalNodeTypeList(),
      default_group_uid=portal.portal_categories.resolveCategory(section_category).getUid(),
    )
  ]
  if not section_uid_list:
    return []
  inventory_list_kw['section_uid'] = section_uid_list
if quantity_unit:
  inventory_list_kw['quantity_unit'] = quantity_unit
if metric_type:
  inventory_list_kw['metric_type'] = metric_type


def makeResultLine(brain):
  """Rewap a brain to propagate inventory kw in getCurrentInventory and getAvailableInventory
  """
  inventory_kw = {
      'node_uid': brain.node_uid,
      'resource_uid': brain.resource_uid,
      'variation_text': brain.variation_text,
  }
  if section_category:
    inventory_kw['section_category'] = section_category
  if quantity_unit:
    inventory_kw['quantity_unit'] = quantity_unit
  if metric_type:
    inventory_kw['metric_type'] = metric_type

  def getCurrentInventory():
    return portal.portal_simulation.getCurrentInventory(**inventory_kw)

  def getAvailableInventory():
    return portal.portal_simulation.getAvailableInventory(**inventory_kw)

  return Object(
      uid='new_',
      node_title=brain.node_title,
      inventory=getattr(brain, 'converted_quantity', brain.inventory),
      getCurrentInventory=getCurrentInventory,
      getAvailableInventory=getAvailableInventory,
      getVariationCategoryItemList=brain.getVariationCategoryItemList,
      variation_category_item_list=[x[0] for x in brain.getObject().getVariationCategoryItemList()],
      getListItemUrl=brain.getListItemUrl,
      getListItemParamDict=brain.getListItemParamDict,
      getListItemUrlDict=brain.getListItemUrlDict,
  )

return [
    makeResultLine(brain)
    for brain in portal.portal_simulation.getFutureInventoryList(
        **inventory_list_kw)
]
