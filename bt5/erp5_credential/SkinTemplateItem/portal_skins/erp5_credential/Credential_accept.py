"""
Intent is to ignore accept/accept race conditions but complain about
any other race condition (ex: accept/reject).

This is intendend to run periodically from an alarm.
"""

if context.getPortalObject().portal_activities.hasActivity(context, only_invalid=True):
  # If this has already failed, no need to try again
  return
if context.getValidationState() != 'accepted':
  context.accept()
