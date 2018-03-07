from zExceptions import Forbidden
if REQUEST is not None:
  raise Forbidden("Request call denied.")

context.BugEvent_sendNotification()
