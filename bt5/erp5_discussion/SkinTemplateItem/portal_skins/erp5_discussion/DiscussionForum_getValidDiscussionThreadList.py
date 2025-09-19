"""
  This script gets list of Discussion Thread for a Forum using predicate search.
"""
return context.searchResults(portal_type='Discussion Thread', sort_on=[('modification_date', 'descending')], validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'))
# couldn't make this work on listbox tales config directly
