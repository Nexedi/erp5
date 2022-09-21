"""
 This script returns the list of Discussion Post objects from the Discussion Thread object
 that is associated to this context.
 If there is no Discussion Thread, an empty list is returned.
"""

if context.getPortalType() != "Discussion Thread":
  discussion = context.DiscussionThread_getContextThread()
else:
  discussion = context

if discussion == None:
  return []

if ("portal_type" in kw) == False:
  kw['portal_type'] = "Discussion Post"

return discussion.searchFolder(**kw)
