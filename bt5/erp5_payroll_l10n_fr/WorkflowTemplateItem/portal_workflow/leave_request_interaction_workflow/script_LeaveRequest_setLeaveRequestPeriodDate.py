leave_request = state_change['object']
for leave_request_period in leave_request.objectValues(portal_type='Leave Request Period'):
  leave_request_period.setEffectiveDate(leave_request.getEffectiveDate())
