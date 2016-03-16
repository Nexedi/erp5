process_list = context.Alarm_getReportResultList()
if len(process_list) > 0:
  return "%s (%s)" % (process_list[0].summary, process_list[0].detail)

return "Unknown"
