"""Unlink simulation movements when delivery movement is deleted.
This way when a delivery movement is deleted, corresponding simulation movement
will again be candidates for building in another delivery.

XXX: security (future) bug: this requires that the system is configured in a way where
simulation movement can be accessed in restrictred mode. For now this script has a proxy
role, but someday we'll have to move this to unrestricted environment.
"""
delivery_movement = state_change['object']

# Always modify movement even if there is no related movement simulation,
# because a concurrent transaction may be linking one to this movement
# (which would modify the local index for "delivery" category).
# In such case, one of the 2 transactions must be restarted.
delivery_movement.serialize()

# Clean simulation
simulation_movement_list = delivery_movement.getDeliveryRelatedValueList(
    portal_type="Simulation Movement")
for simulation_movement in simulation_movement_list:
  if simulation_movement.getDelivery() == delivery_movement.getRelativeUrl():
    simulation_movement.setDelivery(None)
  # 'order' category is deprecated. it is kept for compatibility.
  if simulation_movement.getOrder() == delivery_movement.getRelativeUrl():
    simulation_movement.setOrder(None)

context.DeliveryMovement_updateSimulation(state_change)
