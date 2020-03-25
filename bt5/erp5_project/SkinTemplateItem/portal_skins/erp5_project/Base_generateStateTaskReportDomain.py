return [
  context.Base_generateDomain(parent, 'confirmed', 'Confirmed', 'simulation_state', ['confirmed', 'stopped', 'started']),
  context.Base_generateDomain(parent, 'closed', 'Closed', 'simulation_state', ['delivered'])
]
