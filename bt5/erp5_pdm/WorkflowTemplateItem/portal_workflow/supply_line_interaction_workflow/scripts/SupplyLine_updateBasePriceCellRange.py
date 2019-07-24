supply_line = state_change['object']

# Currently state_change.kwargs['workflow_method_args'] contains
# a list of string, so this script is called every time.
# As it is not the intent, let's return early if nothing changes
if [float(x) for x in sorted(state_change.kwargs['workflow_method_args'][0], key=lambda x: float(x))] == sorted(supply_line.getQuantityStepList()):
  return

if supply_line.isBasePricePerSlice():
  price_parameter = 'slice_base_price'
else:
  price_parameter = 'base_price'
base_id = 'path'
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id=base_id)
