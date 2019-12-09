return [
  context.Base_generateDomain(parent, 'confirmed', 'Confirmed', 'simulation_state', 'confirmed'),
  context.Base_generateDomain(parent, 'not_confirmed', 'Not Confirmed', 'simulation_state', ['planned', 'ordered']),
  context.Base_generateDomain(parent, 'cancelled', 'Cancelled', 'simulation_state', ['cancelled', 'deleted'])
]
