return [
  context.Base_generateDomain(parent, 'opened', 'Opened', 'simulation_state', ['confirmed', 'planned', 'auto_planned', 'ordered']),
  context.Base_generateDomain(parent, 'cancelled', 'Cancelled', 'simulation_state', ['cancelled', 'deleted'])
]
