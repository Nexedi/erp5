"""
 Old forum backward compatibility script, wraps new DiscussionForum_getDiscussionThreadList
"""

# get the related forum using follow_up
result = context.getFollowUpRelatedValueList(portal_type = "Discussion Forum")
valid_states = ('published', 'published_alive', 'released', 'released_alive', 'shared', 'shared_alive')
result = [forum for forum in result if forum.getValidationState() in valid_states]
if result:
  forum = result[0]
else:
  raise ValueError, 'Unable to found a valid Discussion Forum for the current web site/section'

return forum.DiscussionForum_getValidDiscussionThreadList(**kw)
