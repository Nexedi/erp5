data_delivery = context

error_list = []

data_supply_set = set(data_delivery.getSpecialiseValueList(portal_type='Data Supply'))
simulation_state = data_delivery.getSimulationState()

if not data_supply_set:
  validation_state_list = ['deleted']
else:
  validation_state_list = [s.getValidationState() for s in data_supply_set]

if all (validation_state == 'deleted' for validation_state in validation_state_list):
  if simulation_state in ('started', 'stopped'):
    error_list.append("Simulation should be delivered")
    if fixit:
      data_delivery.deliver()
elif simulation_state == 'started' and 'validated' not in validation_state_list:
  error_list.append("Simulation is started but should be stopped")
  if fixit:
    data_delivery.stop()
elif simulation_state == 'stopped' and 'validated' in validation_state_list:
  error_list.append("Simulation is stopped but should be started")
  if fixit:
    data_delivery.start()

return error_list
