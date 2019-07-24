supply_cell = state_change['object']
supply_line = supply_cell.getParentValue()
if supply_cell.getParentValue().isBasePricePerSlice():
  supply_line.updateCellSliceParameterList(base_id='path')
else:
  supply_line.updateCellSliceParameterList(base_id='path')
