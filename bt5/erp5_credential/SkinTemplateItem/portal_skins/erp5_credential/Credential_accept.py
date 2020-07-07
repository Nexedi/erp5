"""
Intent is to ignore accept/accept race conditions but complain about
any other race condition (ex: accept/reject).

This is intendend to run periodically from an alarm.
"""
if context.hasErrorActivity():
  # If this has already failed, no need to try again
  return
if context.getValidationState() != 'accepted':
  context.accept()
