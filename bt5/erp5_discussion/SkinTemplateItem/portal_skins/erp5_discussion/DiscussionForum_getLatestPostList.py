"""
  Get list of latest Posts from a Discussion Forum (Predicate).
  Context: Discussion Forum object.
"""

limit = kw.get("limit", 100)
size = kw.pop("size", None)
if size is not None:
  limit = min(size, limit)

# Discussion Forum IS a Predicate, so searchResults works directly
parent_uid_list = [
  x.uid for x in context.searchResults(
    portal_type='Discussion Thread',
    sort_on=[('modification_date', 'descending')],
    validation_state=('published', 'published_alive', 'released',
                     'released_alive', 'shared', 'shared_alive'))
]

if not parent_uid_list:
  return []

# get sorted list of all "contained" Posts
kw['sort_on'] = (('modification_date', 'DESC'),)
kw['portal_type'] = 'Discussion Post'
kw['parent_uid'] = parent_uid_list
kw['limit'] = limit

return context.portal_catalog(**kw)
