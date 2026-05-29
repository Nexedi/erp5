"""
  Get list of latest Posts which belong to a forum (i.e. websection + predicate)
"""

limit = kw.get("limit", 100)
size = kw.pop("size", None)
if size is not None:
  limit = min(size, limit)

parent_uid_list = None

forum = context.WebSection_getRelatedForum()
if forum:
  # get list of all forum Threads (details should be set on predicate)
  parent_uid_list = [
    x.uid for x in forum.searchResults(portal_type='Discussion Thread',
                                       sort_on=[('modification_date', 'descending')],
                                       validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'))
  ]

if not parent_uid_list:
  # no related forum or
  # no parent discussion threads therefore no posts
  return []

# get sorted list of all "contained" in them Posts
kw['sort_on'] = (('modification_date', 'DESC'),)
kw['portal_type'] = 'Discussion Post'
kw['parent_uid'] = parent_uid_list
kw['limit'] = limit

return context.portal_catalog(**kw)