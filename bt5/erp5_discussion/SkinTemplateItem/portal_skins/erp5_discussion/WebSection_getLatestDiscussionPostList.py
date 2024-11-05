"""
  Get list of latest Posts which belong to a forum (i.e. websection + predicate)
"""
# first get list of all container Threads (details should be set on predicate)
parent_uid_list = [
  x.uid for x in context.getDocumentValueList(
    portal_type="Discussion Thread",
  )
]

if not parent_uid_list:
  # no parent discussion threads therefore no posts
  return []

# get sorted list of all "contained" in them Posts
kw['sort_on'] = (('modification_date', 'DESC'),)
kw['portal_type'] = 'Discussion Post'
kw['parent_uid'] = parent_uid_list

return context.portal_catalog(**kw)
