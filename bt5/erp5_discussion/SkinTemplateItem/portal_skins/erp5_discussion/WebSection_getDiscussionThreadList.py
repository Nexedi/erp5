"""
  This script gets list of Discussion Thread for a Forum using catalog.
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet threads.
"""
thread_relative_url = context.REQUEST.get('thread_relative_url')
discussion_thread_list = [x.getObject() for x  in context.getDocumentValueList(**kw)]
if thread_relative_url is not None:
  thread = context.restrictedTraverse(thread_relative_url)
  if thread is not None and thread not in discussion_thread_list:
    discussion_thread_list = [thread] + discussion_thread_list
return discussion_thread_list
