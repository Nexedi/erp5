"""
  This script gets list of Discussion Thread for a Forum using catalog.
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet threads.
"""

# get the related forum using predicate search
result = context.getFollowUpRelatedValueList(portal_type = "Discussion Forum",
                                             validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'))
if result:
  forum = result[0]
  discussion_thread_list = [x.getObject() for x  in forum.searchResults(portal_type="Discussion Thread",
                                                                        validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'),
                                                                        **kw)]
  thread_relative_url = context.REQUEST.get('thread_relative_url')
  if thread_relative_url is not None:
    thread = forum.restrictedTraverse(thread_relative_url)
    if thread is not None and thread not in discussion_thread_list:
      discussion_thread_list = [thread] + discussion_thread_list
  return discussion_thread_list
else:
  return []
