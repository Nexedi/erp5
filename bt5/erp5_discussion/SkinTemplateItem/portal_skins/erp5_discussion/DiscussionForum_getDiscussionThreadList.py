"""
  This script gets the full list of Discussion Thread for a Forum using predicate search.
"""
size = kw.pop("size", None)
if size is not None:
  kw.setdefault('limit', size)
kw.setdefault('portal_type', 'Discussion Thread')
kw.setdefault('sort_on', [('modification_date', 'descending')])
return context.searchResults(**kw)