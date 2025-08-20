"""
  Get list of latest Posts which belong to a forum (i.e. websection + predicate)
"""
parent_uid_list = None

# first get the related forum using predicate search
result = context.getFollowUpRelatedValueList(portal_type = "Discussion Forum")
valid_states = ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')
result = [forum for forum in result if forum.getValidationState() in valid_states]
if result:
  forum = result[0]
  # get list of all forum Threads (details should be set on predicate)
  parent_uid_list = [
    x.uid for x in forum.searchResults(
      portal_type="Discussion Thread",
    )
  ]

if not parent_uid_list:
  # no related forum or
  # no parent discussion threads therefore no posts
  return []

# get sorted list of all "contained" in them Posts
kw['sort_on'] = (('modification_date', 'DESC'),)
kw['portal_type'] = 'Discussion Post'
kw['parent_uid'] = parent_uid_list

return context.portal_catalog(**kw)
