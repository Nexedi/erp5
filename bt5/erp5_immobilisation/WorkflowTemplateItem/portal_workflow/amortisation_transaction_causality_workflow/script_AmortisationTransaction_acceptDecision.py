transaction = state_change['object']
context.log('acceptDecision script on', transaction)
transaction.portal_simulation.solveDelivery(transaction, "Distribute",
                                             "ProfitAndLoss")
for movement in transaction.getMovementList():
  for simulation_movement in movement.getDeliveryRelatedValueList(portal_type='Simulation Movement'):
    context.log('solving movement', simulation_movement)
    transaction.portal_simulation.solveMovement(simulation_movement, None,
                                             "ProfitAndLoss")

# Automatic workflow
transaction.activate().updateCausalityState()
