"""
Intent is to ignore accept/accept race conditions but complain about
any other race condition (ex: accept/reject).
"""
if context.getValidationState() != 'accepted':
  context.accept()
