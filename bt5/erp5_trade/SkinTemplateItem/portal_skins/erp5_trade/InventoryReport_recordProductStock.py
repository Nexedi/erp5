portal = context.getPortalObject()
getInventoryList = portal.portal_simulation.getInventoryList
newContent = context.newContent
result_dict = {}

for i in getInventoryList(
  section_uid = context.getDestinationSectionUid(),
  node_uid = context.getDestinationUid(),
  group_by_resource = 1,
  #group_by_node = 1,
  group_by_variation = 1,
  group_by_movement = 1,
  resourceType=portal.getPortalProductTypeList(),
  at_date = context.getStartDate()
  ):
  resource = i.getResource()
  variation_text = i.variation_text
  total_quantity = i.total_quantity
  key = (resource, variation_text)
  (tmp_quantity, tmp_price) = result_dict.get(key, (0, 0))
  if total_quantity > 0:
    total_price = i.getDestinationAssetPrice() * total_quantity
  else:
    total_price = i.getSourceAssetPrice() * total_quantity
  result_dict[key] = (tmp_quantity + total_quantity, tmp_price + total_price)

for (resource, variation_text), (total_quantity, total_price) in result_dict.iteritems():
  inventory_line = newContent(portal_type='Inventory Report Line')
  inventory_line.edit(
  resource = resource,
  total_price = total_price,
  variation_category_list = variation_text,
  total_quantity = total_quantity)

context.record()
