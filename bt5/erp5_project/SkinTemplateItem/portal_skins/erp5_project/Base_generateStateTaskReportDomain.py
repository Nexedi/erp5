return [
  context.Base_generateDomain(parent, 'confirmed', 'Confirmed', 'simulation_state', 'confirmed'),
  context.Base_generateDomain(parent, 'closed', 'Closed', 'simulation_state', ['delivered', 'stopped'])
]
