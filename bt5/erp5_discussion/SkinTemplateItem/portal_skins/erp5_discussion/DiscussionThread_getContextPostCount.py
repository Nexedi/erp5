""" This script returns the number of Discussion Post objects from the Discussion Thread 
 object that is associated to this context.
 If there is no Discussion Thread, 0 is returned."""
discussion = context.DiscussionThread_getContextThread()

if discussion == None:
  return 0

return discussion.countFolder(portal_type='Discussion Post')[0][0]
