"""
  This script gets list of Discussion Thread for a Forum using catalog.
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet threads.
"""
thread_relative_url = context.REQUEST.get('thread_relative_url')
# backward compatibility for web section (this should be dropped)
if context.getPortalType() == 'Web Section':
  related_forum_url = context.follow_up
  if related_forum_url is not None:
    forum = context.restrictedTraverse(related_forum_url)
    discussion_thread_list = [x.getObject() for x  in forum.getDocumentValueList(**kw)] #searches in all erp5 docs linked to this predicate config
  else:
    discussion_thread_list = []
if context.getPortalType() == 'Discussion Forum':
  forum = context
  discussion_thread_list = [x.getObject() for x  in forum.getDocumentValueList(**kw)] #searches in all erp5 docs linked to this predicate config

if thread_relative_url is not None:
  thread = forum.restrictedTraverse(thread_relative_url)
  if thread is not None and thread not in discussion_thread_list:
    discussion_thread_list = [thread] + discussion_thread_list
return discussion_thread_list
