delivery = state_change['object'].getParentValue()
if delivery.isDelivery:
  delivery.updateSimulation(expand_related=1)
