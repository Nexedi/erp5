movement = state_change['object']
if not movement.hasBaseUnitPrice():
  base_unit_price = state_change['kwargs']['workflow_method_result']
  if base_unit_price is not None:
    movement.setBaseUnitPrice(base_unit_price)
