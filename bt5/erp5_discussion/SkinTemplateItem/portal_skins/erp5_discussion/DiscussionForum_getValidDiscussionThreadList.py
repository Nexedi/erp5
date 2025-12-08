"""
  This script gets the list of valid Discussion Thread for a Forum using predicate search.
"""

kw.setdefault('portal_type', 'Discussion Thread')
kw.setdefault('sort_on', [('modification_date', 'descending')])
kw.setdefault('validation_state', ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'))
return context.searchResults(**kw)
