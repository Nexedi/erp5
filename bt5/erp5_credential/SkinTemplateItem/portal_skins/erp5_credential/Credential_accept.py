"""
Intent is to ignore accept/accept race conditions but complain about
any other race condition (ex: accept/reject).

This is intendend to run periodically from an alarm.
"""
if context.hasActivity():
  return
if context.getValidationState() != 'accepted':
  context.accept()
