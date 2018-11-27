portal = context.getPortalObject()
getInventoryList = portal.portal_simulation.getInventoryList
newContent = context.newContent
result_list = getInventoryList(
  section_uid = context.getDestinationSectionUid(),
  node_uid = context.getDestinationUid(),
  group_by_resource = 1,
  group_by_node = 1,
  resourceType=portal.getPortalProductTypeList()
  )

for i in result_list:
  inventory_line = newContent(portal_type='Inventory Line')
  inventory_line.edit(
  resource = i.getResource(),
  total_price = i.total_price,
  quantity = i.total_quantity)

context.record()
