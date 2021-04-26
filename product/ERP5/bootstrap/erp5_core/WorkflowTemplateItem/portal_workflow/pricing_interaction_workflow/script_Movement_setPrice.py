movement = state_change['object']
if not movement.hasPrice():
  price = state_change['kwargs']['workflow_method_result']
  if price is not None:
    movement.setPrice(price)
