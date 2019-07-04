supply_cell = state_change['object']
if supply_cell.getParentValue().isBasePricePerSlice():
  supply_cell.setSliceBasePrice(supply_cell.getBasePrice())
else:
  supply_cell.setSliceBasePrice(None)
