transaction = state_change['object']

# Set relative simulation movements profit_quantity to 0
movement_list = transaction.getMovementList()
all_simulation_movement_path_list = []
for movement in movement_list:
  simulation_movement_list = movement.getDeliveryRelatedValueList(portal_type='Simulation Movement')
  for simulation_movement in simulation_movement_list:
    simulation_movement.edit(profit_quantity=0)
  all_simulation_movement_path_list.extend([x.getPath() for x in simulation_movement_list])

# Update from simulation, then adapt causality value
builder = transaction.portal_deliveries.amortisation_transaction_builder
builder.updateFromSimulation(transaction.getRelativeUrl())
tag = '%s_afterBuild' % transaction.getRelativeUrl()
transaction.activate(tag=tag,
    after_path_and_method_id=(
    all_simulation_movement_path_list,
    ('immediateReindexObject', 'recursiveImmediateReindexObject'))).AmortisationTransaction_afterBuild()

# Automatic workflow
transaction.activate(after_tag=tag).updateCausalityState()
