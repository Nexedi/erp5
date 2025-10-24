"""
 Old forum backward compatibility script, returns the related forum object created during the migration, using predicate search
"""

valid_states = ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')
result = [x.getObject() for x  in context.searchResults(portal_type='Discussion Forum', validation_state=valid_states)]
if result:
  return result[0]
else:
  raise ValueError, 'Unable to found a valid Discussion Forum for the current web site/section'
