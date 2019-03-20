portal = context.getPortalObject()
getCurrentInventoryList = portal.portal_simulation.getCurrentInventoryList

section_uid = context.getDestinationSectionUid()
node_uid = context.getDestinationUid()
to_date = context.getStartDate()
resource = []
for key in aggregate_dict:
  resource.append(key[0])

current_inventory_list =  getCurrentInventoryList(
  section_uid = section_uid,
  node_uid = node_uid,
  resource_uid = resource,
  to_date = to_date,
  group_by_sub_variation = 1,
  group_by_variation = 1,
  group_by_resource = 1)

new_list = []
for inventory in current_inventory_list:
  key = tuple([inventory.resource_uid, inventory.variation_text])
  aggregate_value = aggregate_dict.get(key, None)
  if aggregate_value:
    if inventory.sub_variation_text not in aggregate_value:
      new_list.append(inventory)
 

for inventory in new_list:
  inventory_offset_line = context.newContent(portal_type='Inventory Offset Line')
  inventory_offset_line.edit(
    resource_uid = inventory.resource_uid)
  if inventory.variation_text:
    inventory_offset_line.setVariationCategoryList(inventory.variation_text.split('\n'))
    cell_key = [inventory.variation_text]
    cell = inventory_offset_line.newCell(base_id='movement',
                             portal_type='Inventory Offset Cell',
                             *cell_key
                          )
    cell.edit(mapped_value_property_list=['quantity'],
                quantity =  - inventory.quantity,
                predicate_category_list=cell_key,
                variation_category_list=cell_key,)
    
    cell.setAggregateValueList(inventory.sub_variation_text.split('\n'))
  else:
    inventory_offset_line.setAggregateValueList(inventory.sub_variation_text.split('\n'))
    inventory_offset_line.setQuantity(- inventory.quantity)
