return [
  context.Base_generateDomain(parent, 'open', 'Open', 'simulation_state', ['confirmed', 'ready', 'stopped']),
  context.Base_generateDomain(parent, 'closed', 'Closed', 'simulation_state', ['delivered']),
  context.Base_generateDomain(parent, 'not_started', 'Cancelled', 'simulation_state', ['cancelled'])
]
