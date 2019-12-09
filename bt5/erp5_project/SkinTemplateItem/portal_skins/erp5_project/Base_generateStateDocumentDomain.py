return [
  context.Base_generateDomain(parent, 'confirmed', 'Confirmed', 'validation_state', ['shared', 'released', 'published', 'shared_alive', 'released_alive', 'published_alive']),
  context.Base_generateDomain(parent, 'not_confirmed', 'Not Confirmed', 'validation_state', ['submitted', 'requested', 'assigned', 'translated', 'split']),
  context.Base_generateDomain(parent, 'archived_discarded', 'Archived/Discarded', 'validation_state', ['archived', 'deleted', 'cancelled', 'hidden'])
]
