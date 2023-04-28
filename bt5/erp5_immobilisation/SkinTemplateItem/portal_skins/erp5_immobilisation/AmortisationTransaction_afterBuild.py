# Set causality value to items which generated the simulation movements
causality_value_list = []
for movement in context.getMovementList():
  simulation_movement_list = movement.getDeliveryRelatedValueList()
  for simulation_movement in simulation_movement_list:
    applied_rule = simulation_movement.getParentValue()
    item_list = applied_rule.getCausalityValueList()
    if len(item_list) > 0:
      item = item_list[0]
      if not item in causality_value_list:
        causality_value_list.append(item)

  # Special behavior since expand may disconnect some movements
  # Set quantity to 0 if no movement connected, and check each simulation
  # movement real divergence
  if len(simulation_movement_list) == 0:
    movement.edit(quantity=0)
  else:
    total_quantity = 0
    for simulation_movement in simulation_movement_list:
      total_quantity += simulation_movement.getCorrectedQuantity()
    if total_quantity == 0:
      for simulation_movement in simulation_movement_list:
        simulation_movement.edit(delivery_ratio=1, activate_kw={'tag':'after_amortisation_build'})

if context.getSimulationState() in context.getPortalUpdatableAmortisationTransactionStateList():
  context.edit(causality_value_list=causality_value_list)
  # Update causality state
  #Test Add by Nicolas
  if getattr(context, 'startBuilding', None) is not None:
    context.startBuilding()
  context.activate(activity='SQLDict', after_tag='after_amortisation_build').updateCausalityState()
