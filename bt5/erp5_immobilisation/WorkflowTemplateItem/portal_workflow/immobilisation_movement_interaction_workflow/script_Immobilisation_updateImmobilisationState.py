movement_content = state_change['object']
#movement_content.log(movement_content.getRelativeUrl())
movement = movement_content.getRootDeliveryValue()
if getattr(movement, 'getImmobilisationState', None) is not None and movement.getImmobilisationState() != 'calculating':
  movement.calculateImmobilisationValidity()
