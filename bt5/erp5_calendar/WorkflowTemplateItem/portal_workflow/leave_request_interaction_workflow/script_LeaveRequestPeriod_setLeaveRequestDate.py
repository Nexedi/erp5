leave_request = state_change['object'].getParentValue()
leave_request_period_list = leave_request.objectValues(
  portal_type='Leave Request Period',
)
leave_request.setStartDate(
  min([x.getStartDate() for x in leave_request_period_list])
)
leave_request.setStopDate(
  max([x.getStopDate() for x in leave_request_period_list])
)
