supply_line = state_change['object']

if supply_line.isBasePricePerSlice():
  price_parameter = 'slice_base_price'
else:
  price_parameter = 'base_price'
base_id = 'path'
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id=base_id)
