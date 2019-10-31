return [
         context.Base_generateDomain(parent, 'validated', 'Validated', 'simulation_state', 'validated'),
         context.Base_generateDomain(parent, 'not_validated', 'Not Validated', 'simulation_state', ['submitted', 'suspended', 'draft', 'invalidated']),
         context.Base_generateDomain(parent, 'cancelled', 'Cancelled', 'simulation_state', ['cancelled', 'deleted'])
       ]
