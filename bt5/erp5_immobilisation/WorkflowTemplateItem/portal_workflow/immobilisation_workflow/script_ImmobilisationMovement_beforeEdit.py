pl = state_change['object']
#pl.log(pl.getRelativeUrl())
for movement in pl.getAggregatedItemsNextImmobilisationMovementValueList():
  if movement.getImmobilisationState() != 'calculating':
    movement.calculateImmobilisationValidity()
