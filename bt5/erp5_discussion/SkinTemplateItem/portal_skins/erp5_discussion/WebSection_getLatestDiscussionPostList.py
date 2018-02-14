"""
  Get list of latest Posts which belong to a forum (i.e. websection + predicate)
"""
# first get list of all container Threads (details should be set on predicate)
parent_uid_list = [x.getUid() for x in context.getDocumentValueList()]

# get sorted list of all "contained" in them Posts
kw['sort_on'] = (('modification_date', 'DESC'),)
kw['portal_type'] = 'Discussion Post'
kw['parent_uid'] = parent_uid_list

if len(parent_uid_list)==0:
  # no parent discussion threads therefore no posts
  return []

return context.portal_catalog(**kw)
