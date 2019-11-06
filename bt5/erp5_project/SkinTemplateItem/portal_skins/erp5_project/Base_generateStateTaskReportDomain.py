return [
         context.Base_generateDomain(parent, 'started', 'Confirmed', 'simulation_state', 'confirmed'),
         context.Base_generateDomain(parent, 'not_started', 'Not Confirmed', 'simulation_state', 'draft'),
         context.Base_generateDomain(parent, 'closed', 'Closed', 'simulation_state', ['delivered', 'stopped'])
       ]
