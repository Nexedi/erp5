movement = state_change['object']

resource = movement.getResourceValue()
if resource is not None:
  # quantity unit can be acquired from resource.
  # (Amount class has getQuantityUnit method for backward compatibility and it tries to acquire value from resource).
  if movement.hasCategory('quantity_unit'):
    # if the movement already have a quantity unit which is valid for this resource, don't change it
    movement_quantity_unit = movement.getQuantityUnit()
    if movement_quantity_unit and movement_quantity_unit in resource.getQuantityUnitList():
      return
  # otherwise initialise to the default quantity unit
  movement.setQuantityUnit(resource.getDefaultQuantityUnit())
