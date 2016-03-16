packing_list = state_change['object']

for movement in packing_list.getMovementList():
  movement.setQuantity(movement.Movement_getPackedQuantity())

packing_list.edit()
