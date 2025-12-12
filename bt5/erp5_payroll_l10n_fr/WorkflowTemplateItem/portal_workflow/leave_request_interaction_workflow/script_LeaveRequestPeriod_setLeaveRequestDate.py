leave_request = state_change['object'].getParentValue()
leave_request_period_list = leave_request.objectValues(
  portal_type='Leave Request Period',
)


min_start_date = None
max_stop_date = None

for x in leave_request_period_list:
  start_date = x.getStartDate()
  if start_date:
    if not min_start_date:
      min_start_date = start_date
    elif min_start_date > start_date:
        min_start_date = start_date

  stop_date = x.getStopDate()
  if stop_date:
    if not max_stop_date:
      max_stop_date = stop_date
    elif max_stop_date < stop_date:
      max_stop_date = stop_date

leave_request.edit(
  start_date = min_start_date,
  stop_date = max_stop_date
)
