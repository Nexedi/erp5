"""
  Send email to all [project members after a Dicusssion Thread gets edited.
  It gets edited when real edit happens or when a new Discussion Post is added.
  XXX: implement for corresponding projects.
"""
from zExceptions import Unauthorized

try:
  follow_up = context.getFollowUpValue()
except Unauthorized:
  follow_up = None

def getPersonWithEmailReferenceSet():
  # breaks if follow_up is None
  return set([
    x.getUserId()
    for x in [ # person_list
      x.getParentValue()
      for x in context.portal_catalog(
        portal_type='Assignment',
        destination_project_uid=follow_up.getUid(),
        validation_state='open',
      )]
    if x.getDefaultEmailText() not in ("", None)
  ])

return

# Template example:

# check follow_up.getRelativeUrl() # project
#  message = "New forum post created..."
#  subject = "[Project] New forum post created."
#  for reference in getPersonWithEmailReferenceSet():
#    context.portal_notifications.activate(activity='SQLQueue').sendMessage(...)
