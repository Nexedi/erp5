portal = context.getPortalObject()
getInventoryList = portal.portal_simulation.getInventoryList
product_list = portal.getPortalProductTypeList()

result_list = getInventoryList(
  section_uid = context.getDestinationSectionUid(),
  node_uid = context.getDestinationUid(),
  group_by_resource = 1,
  group_by_node = 1
  )

for i in result_list:
  resource = i.getResource()
  if resource:
    resource = portal.restrictedTraverse(resource)
    if resource.getPortalType() in product_list:
      inventory_line = context.newContent(portal_type='Inventory Line')
      inventory_line.edit(
        resource = i.getResource(),
        total_price = i.total_price,
        quantity = i.total_quantity)

context.record()
