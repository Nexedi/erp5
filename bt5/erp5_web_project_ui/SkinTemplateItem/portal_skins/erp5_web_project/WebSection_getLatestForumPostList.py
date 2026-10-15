"""
  Rows for the aggregated forum feed: the latest Discussion Posts of every project the
  requesting user may read, newest first.
  Context: the aggregated feed Web Section.

  NO _proxy_roles on purpose: the scoping to "the projects I have access to" IS the catalog
  security of the requesting user. Elevating this script would return every forum of the
  portal to everybody.

  A Discussion Post has no publication workflow and the catalog has no parent_validation_state
  related key, so the thread state is applied with a second query over the parent uids.
"""

# both can arrive as strings when passed through the listbox from the URL
limit = int(kw.pop("limit", 20))
size = int(kw.pop("size", limit))
limit = min(size, limit)

portal = context.getPortalObject()

kw['portal_type'] = 'Discussion Post'
kw['parent_portal_type'] = 'Discussion Thread'
kw['sort_on'] = (('modification_date', 'DESC'),)
kw['limit'] = limit
# selected to filter on the parent below without loading every post
kw['select_list'] = ('catalog.parent_uid',)

post_list = portal.portal_catalog(**kw)
if not post_list:
  return []

parent_uid_dict = {}
for post in post_list:
  parent_uid_dict[post.parent_uid] = 1

# same states as the per-forum feed, DiscussionForum_getLatestDiscussionPostList
thread_uid_dict = {}
for thread in portal.portal_catalog(
    portal_type='Discussion Thread',
    uid=list(parent_uid_dict.keys()),
    validation_state=('published', 'published_alive', 'released',
                      'released_alive', 'shared', 'shared_alive')):
  thread_uid_dict[thread.uid] = 1

return [post for post in post_list if post.parent_uid in thread_uid_dict]
