portal = context.getPortalObject()
getCurrentInventoryList = portal.portal_simulation.getCurrentInventoryList
newContent = context.newContent
section_uid = context.getDestinationSectionUid()
node_uid = context.getDestinationUid()
to_date = context.getStartDate()

for inventory in getCurrentInventoryList(
  section_uid = section_uid,
  node_uid = node_uid,
  group_by_resource = 1,
  group_by_variation = 1,
  group_by_sub_variation = 1,
  resourceType=portal.getPortalProductTypeList(),
  to_date = to_date,
  
):
  if inventory.total_quantity:
    if tuple([inventory.getResource(), inventory.variation_text]) in excluded_list:
      continue
    inventory_offset_line = newContent(portal_type='Inventory Offset Line')
    inventory_offset_line.edit(resource = inventory.getResource())
    if not inventory.variation_text:
      inventory_offset_line.edit(
        quantity = -inventory.total_quantity
      )
    else:
      inventory_offset_line.setVariationCategoryList(inventory.variation_text)
      base_id = 'movement'
      for cell_key in inventory_offset_line.getVariationCategoryList():
        cell_key = [cell_key]
        cell = inventory_offset_line.newCell(base_id=base_id,
                                             portal_type='Inventory Offset Cell',
                                             *cell_key)
        cell.edit(mapped_value_property_list=['quantity'],
                  quantity= -inventory.total_quantity,
                  predicate_category_list=cell_key,
                  variation_category_list=cell_key,)
