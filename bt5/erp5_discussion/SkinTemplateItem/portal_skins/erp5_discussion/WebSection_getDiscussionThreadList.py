"""
 Old forum backward compatibility script
  This script gets list of Discussion Thread for a Forum using predicate search
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet threads.
"""
from zExceptions import Unauthorized

forum = context.WebSection_getRelatedForum()
thread_relative_url = context.REQUEST.get('thread_relative_url')
try:
  discussion_thread_list = [x.getObject() for x  in forum.searchResults(portal_type='Discussion Thread',
                                                                        sort_on=[('modification_date', 'descending')],
                                                                        validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'))]
except Unauthorized:
  discussion_thread_list = []
if thread_relative_url is not None:
  thread = context.restrictedTraverse(thread_relative_url)
  if thread is not None and thread not in discussion_thread_list:
    discussion_thread_list = [thread] + discussion_thread_list
return discussion_thread_list
