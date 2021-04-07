pl = state_change['object']

# It is done before and after because stop_date may have change
for movement in pl.getAggregatedItemsNextImmobilisationMovementValueList():
  if movement.getImmobilisationState() != 'calculating':
    movement.calculateImmobilisationValidity()

pl.activate(after_method_id=('recursiveReindexObject', 'immediateReindexObject',)).updateImmobilisationState()
