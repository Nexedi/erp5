if not inventory_line:
  return
portal = context.getPortalObject()
inventory_line = portal.restrictedTraverse(inventory_line)
inventory = context.getParentValue()

getCurrentInventory = portal.portal_simulation.getCurrentInventory

section_uid = inventory.getDestinationSectionUid()
node_uid = inventory.getDestinationUid()

to_date = inventory.getStartDate()
inventory_cell_list = inventory_line.contentValues(portal_type='Inventory Cell')

if len(inventory_cell_list):
  context.setVariationCategoryList(inventory_line.getVariationCategoryList())
  context.setQuantityUnitValue(inventory_line.getQuantityUnitValue())
  base_id = 'movement'
  for inventory_cell in inventory_cell_list:
    cell_key = inventory_cell.getVariationCategoryList()
    sub_variation_text = inventory_cell.getSubVariationText()
    quantity = getCurrentInventory(
      section_uid = section_uid,
      node_uid = node_uid,
      to_date = to_date,
      resource = context.getResource(),
      variation_text = inventory_cell.getVariationText(),
      sub_variation_text = sub_variation_text
      )
    cell = context.newCell(base_id=base_id,
                           portal_type='Inventory Offset Cell',
                           *cell_key
                          )
    cell.edit(mapped_value_property_list=['quantity', 'price'],
              quantity=inventory_cell.getQuantity() - quantity,
              price = inventory_cell.getPrice(),
              predicate_category_list=cell_key,
              variation_category_list=cell_key,)
    cell.setAggregateValueList(inventory_cell.getAggregateValueList())

else:
  quantity = getCurrentInventory(
    section_uid = section_uid,
    node_uid = node_uid,
    to_date = to_date,
    resource = context.getResource())
  context.edit(
    aggregate_value_list = inventory_line.getAggregateValueList(),
    quantity = inventory_line.getQuantity() - quantity,
    price = inventory_line.getPrice())
