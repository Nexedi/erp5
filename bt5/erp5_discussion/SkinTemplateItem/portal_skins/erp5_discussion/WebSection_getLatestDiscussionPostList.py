"""
 Old forum backward compatibility script, wraps new DiscussionForum_getLatestPostList
"""

forum = context.WebSection_getRelatedForum()
return forum.DiscussionForum_getLatestPostList(**kw)
