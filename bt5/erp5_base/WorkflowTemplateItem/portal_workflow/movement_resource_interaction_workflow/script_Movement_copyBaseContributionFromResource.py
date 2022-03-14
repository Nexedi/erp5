movement = state_change['object']

resource = movement.getResourceValue()
if resource is not None:
  # We can over-write base contribution list always.
  # Because when we change the resource, we need to set all the base contribution into movement.
  # Imagine that we buy a product which have complex tax definitions with discounting.
  movement.setBaseContributionList(resource.getBaseContributionList())
