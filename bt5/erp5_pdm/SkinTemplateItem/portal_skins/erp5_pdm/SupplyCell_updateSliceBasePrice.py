quantity_criterion_list = [
  criterion for criterion in context.getCriterionList()
  if criterion.property == 'quantity'
]
if not quantity_criterion_list:
  return
quantity_criterion, = quantity_criterion_list
supply_line_value = context.getParentValue()
if supply_line_value.isBasePricePerSlice():
  quantity_step_list = [None] + supply_line_value.getQuantityStepList(base_id='path') + [None]
  try:
    index = quantity_step_list.index(quantity_criterion.min)
  except ValueError:
    # _range_criterion is set to {} if criterion is None
    index = 0
  min_quantity = quantity_step_list[index]
  max_quantity = quantity_step_list[index+1]
  context.setSliceQuantityRange((min_quantity, max_quantity))
  context.setSliceBasePrice(context.getBasePrice())
else:
  context.setSliceQuantityRange(None)
  context.setSliceBasePrice(None)
