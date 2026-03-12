"""
 Old forum backward compatibility script, wraps new DiscussionForum_getLatestDiscussionPostList
"""

forum = context.WebSection_getRelatedForum()
return forum.DiscussionForum_getLatestDiscussionPostList(**kw)
