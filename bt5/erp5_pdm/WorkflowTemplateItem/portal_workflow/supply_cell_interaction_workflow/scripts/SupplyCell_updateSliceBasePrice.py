supply_cell = state_change['object']
supply_line = supply_cell.getParentValue()
quantity_criterion_list = [
  criterion for criterion in supply_cell.getCriterionList()
  if criterion.property == 'quantity'
]
if len(quantity_criterion_list) == 1:
  quantity_criterion = quantity_criterion_list[0]
else:
  return
if supply_cell.getParentValue().isBasePricePerSlice():
  quantity_step_list = [None] + supply_line.getQuantityStepList(base_id='path') + [None]
  try:
    index = quantity_step_list.index(quantity_criterion.min)
  except KeyError:
    # _range_criterion is set to {} if criterion is None
    index = 0
  min_quantity = quantity_step_list[index]
  max_quantity = quantity_step_list[index+1]
  supply_cell.setSliceQuantityRange((min_quantity, max_quantity))
  supply_cell.setSliceBasePrice(supply_cell.getBasePrice())
else:
  supply_cell.setSliceQuantityRange(None)
  supply_cell.setSliceBasePrice(None)
