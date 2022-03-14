transaction = state_change['object']
# Set relative simulation movements profit_quantity to 0
relative_url = transaction.getRelativeUrl()
indexation_tag = script.id + '_' + relative_url
for movement in transaction.getMovementList():
  for simulation_movement in movement.getDeliveryRelatedValueList(portal_type='Simulation Movement'):
    simulation_movement.edit(profit_quantity=0, activate_kw={'tag': indexation_tag})

# Update from simulation, then adapt causality value
transaction.getPortalObject().portal_deliveries.amortisation_transaction_builder.updateFromSimulation(transaction.getRelativeUrl())
tag = relative_url + '_afterBuild'
transaction.activate(tag=tag, after_tag=indexation_tag).AmortisationTransaction_afterBuild()

# Automatic workflow
transaction.activate(after_tag=tag).updateCausalityState()
