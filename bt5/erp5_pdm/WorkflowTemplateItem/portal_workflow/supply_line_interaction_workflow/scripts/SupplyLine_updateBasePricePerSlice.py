supply_line = state_change['object']
supply_line.updateQuantityPredicate(
  'slice_base_price'
  if supply_line.isBasePricePerSlice() else
  'base_price'
)
supply_line.updateCellRange(base_id='path')
for cell_value in supply_line.getCellValueList(base_id='path'):
  # XXX: only to trigger supply_cell_interaction_workflow/scripts/SupplyCell_updateSliceBasePrice
  cell_value.setBasePrice(cell_value.getBasePrice())
