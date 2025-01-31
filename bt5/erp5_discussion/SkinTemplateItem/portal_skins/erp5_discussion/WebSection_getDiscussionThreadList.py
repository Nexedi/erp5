"""
  This script gets list of Discussion Thread for a Forum using catalog.
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet threads.
"""

forum = context.getDestinationValue()
if forum is not None:
  discussion_thread_list = [x.getObject() for x  in forum.searchResults(**kw)] #searches in all erp5 docs linked to this predicate config
  thread_relative_url = context.REQUEST.get('thread_relative_url')
  if thread_relative_url is not None:
    thread = forum.restrictedTraverse(thread_relative_url)
    if thread is not None and thread not in discussion_thread_list:
      discussion_thread_list = [thread] + discussion_thread_list
  return discussion_thread_list
else:
  return []
