"""
  This script gets list of Discussion Thread for a Forum using predicate search.
"""
return context.searchResults(portal_type='Discussion Thread', sort_on=[('modification_date', 'descending')])
# couldn't make this work on listbox tales config directly
