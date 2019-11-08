return [
  context.Base_generateDomain(parent, 'started', 'Open', 'simulation_state', ['confirmed', 'ready']),
  context.Base_generateDomain(parent, 'closed', 'Solved/Closed', 'simulation_state', ['delivered', 'stopped']),
  context.Base_generateDomain(parent, 'not_started', 'Not Confirmed', 'simulation_state', ['draft', 'cancelled'])
]
