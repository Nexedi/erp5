pl = state_change['object']

for movement in pl.getRootDeliveryValue().getAggregatedItemsNextImmobilisationMovementValueList():
  if movement.getImmobilisationState() != 'calculating':
    movement.calculateImmobilisationValidity()
  else:
    movement.updateImmobilisationState()
pl.ImmobilisationDelivery_expandAggregatedItems()
