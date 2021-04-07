from DateTime import DateTime
group_calendar_assignment = state_change["object"]
stop_date = group_calendar_assignment.getStopDate()
if stop_date:
  stop_date = DateTime(stop_date.Date() + " 23:59:59")
  group_calendar_assignment.setStopDate(stop_date)
