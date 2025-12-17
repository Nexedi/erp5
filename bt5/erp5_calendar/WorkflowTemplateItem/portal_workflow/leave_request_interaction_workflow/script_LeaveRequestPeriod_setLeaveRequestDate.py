leave_request = state_change['object'].getParentValue()
leave_request_period_list = leave_request.objectValues(
  portal_type='Leave Request Period',
)

start_date_list = [x.getStartDate() for x in leave_request_period_list if x.getStartDate()]
if start_date_list:
  leave_request.setStartDate(
    min(start_date_list)
  )
stop_date_list = [x.getStopDate() for x in leave_request_period_list if x.getStopDate()]
if stop_date_list:
  leave_request.setStopDate(
    max(stop_date_list)
  )
