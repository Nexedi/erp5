movement = state_change['object']

resource = movement.getResourceValue()
if resource is not None:
  # quantity unit can be acquired from resource (see Amount.getQuantityUnit)
  # we check that it's really set on the movement.
  if movement.hasQuantityUnit():
    # if the movement already have a quantity unit which is valid for this resource, don't change it
    if movement.getQuantityUnit() not in resource.getQuantityUnitList():
      movement.setQuantityUnit(resource.getDefaultQuantityUnit())
  else:
    # initialise to the default quantity unit
    movement.setQuantityUnit(resource.getDefaultQuantityUnit())

  # if the movement already have a use which is valid for this resource, don't change it.
  # ( unlike quantity unit, use is not acquired )
  if movement.getUse() not in resource.getUseList():
    # otherwise initialise to the default use
    movement.setUse(resource.getDefaultUse())

  # We can over-write base contribution list always.
  # Because when we change the resource, we need to set all the base contribution into movement.
  # Imagine that we buy a product which have complex tax definitions with discounting.
  movement.setBaseContributionList(resource.getBaseContributionList())
