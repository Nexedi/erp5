"""
 Old forum backward compatibility script
  This script gets list of Discussion Thread for a Forum using predicate search
  Due to asynchronous nature of catalog it can use
  passed from REQUEST not index yet threads.
"""

# get the related forum using follow_up
result = context.getFollowUpRelatedValueList(portal_type = "Discussion Forum")
valid_states = ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')
result = [forum for forum in result if forum.getValidationState() in valid_states]
if result:
  forum = result[0]
else:
  raise ValueError, 'Unable to found a valid Discussion Forum for the current web site/section'

thread_relative_url = context.REQUEST.get('thread_relative_url')
discussion_thread_list = [x.getObject() for x  in context.searchResults(portal_type='Discussion Thread', sort_on=[('modification_date', 'descending')], validation_state=('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive'))]
if thread_relative_url is not None:
  thread = context.restrictedTraverse(thread_relative_url)
  if thread is not None and thread not in discussion_thread_list:
    discussion_thread_list = [thread] + discussion_thread_list
return discussion_thread_list
