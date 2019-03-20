document = state_change['object']
tag = '%s:OffsetLineUpdateOffsetQuantity' % document.getRelativeUrl()
excluded_list = []
aggregate_dict = {}
for inventory_line in document.contentValues(portal_type = 'Inventory Line'):
  inventory_offset_line = document.newContent(
    portal_type='Inventory Offset Line',
    resource = inventory_line.getResource()
    )
  excluded_list.append(tuple([inventory_line.getResource(), inventory_line.getVariationText()]))
  inventory_offset_line.activate(tag=tag).InventoryOffsetLine_updateOffsetQuantity(inventory_line = inventory_line.getRelativeUrl())
  inventory_cell_list = inventory_line.contentValues(portal_type='Inventory Cell')
  if len(inventory_cell_list):
    for cell in inventory_cell_list:
      key = tuple([inventory_line.getResourceUid(),cell.getVariationText()])
      if aggregate_dict.get(key, None) is None:
        aggregate_dict[key] = []
      aggregate_dict[key].append(cell.getSubVariationText())
  else:
    aggregate_dict[tuple([inventory_line.getResourceUid(), ''])] = ['']


document.activate(tag=tag).Inventory_createOffsetLineForNotPresentAggregateInventory(aggregate_dict = aggregate_dict)


if document.isFullInventory():
  document.activate(tag=tag).Inventory_createOffsetLineForUselessInventory(excluded_list = excluded_list)

document.calculate()
document.activate(after_tag = tag).record()
