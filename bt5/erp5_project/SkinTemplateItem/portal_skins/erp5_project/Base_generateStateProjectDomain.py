return [
  context.Base_generateDomain(parent, 'started', 'Started', 'validation_state', 'validated'),
  context.Base_generateDomain(parent, 'not_started', 'Not Started', 'validation_state', ['draft', 'invalidated', 'suspended'])
]
