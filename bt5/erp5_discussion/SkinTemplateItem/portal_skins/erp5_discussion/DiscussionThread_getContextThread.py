"""This script returns ththe Discussion Thread object that is associated to this context.
Or the first if many.
If there is no Discussion Thread, return None.
Need a proxy to work correctly with anonymous user"""

discussion = context.getFollowUpRelated(portal_type = "Discussion Thread")

if discussion is not None:
  discussion = context.restrictedTraverse(discussion, None)

return discussion
