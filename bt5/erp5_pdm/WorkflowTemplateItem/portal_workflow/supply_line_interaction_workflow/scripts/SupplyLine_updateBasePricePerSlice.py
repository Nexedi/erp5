supply_line = state_change['object']
to_delete_cell_list = [
  cell for cell in supply_line.getCellIdList(base_id='path')
  if hasattr(supply_line, cell)
]
supply_line.manage_delObjects(ids=to_delete_cell_list)
if state_change.kwargs['workflow_method_args'][0]:
  price_parameter = 'slice_base_price'
else:
  price_parameter = 'base_price'
supply_line.updateQuantityPredicate(price_parameter)
supply_line.updateCellRange(base_id='path')
