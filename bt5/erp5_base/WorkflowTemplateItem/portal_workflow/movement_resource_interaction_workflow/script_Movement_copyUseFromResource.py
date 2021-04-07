movement = state_change['object']

resource = movement.getResourceValue()
if resource is not None:
  # if the movement already have a use which is valid for this resource, don't change it
  movement_use = movement.getUse()
  if movement_use and movement_use in resource.getUseList():
    return
  # otherwise initialise to the default use
  movement.setUse(resource.getDefaultUse())
