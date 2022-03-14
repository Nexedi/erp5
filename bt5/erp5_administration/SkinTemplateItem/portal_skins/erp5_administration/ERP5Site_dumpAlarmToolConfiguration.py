from builtins import str
alarm_tool = context.getPortalObject().portal_alarms
periodicity_list = [
  'periodicity_day_frequency',
  'periodicity_hour',
  'periodicity_hour_frequency',
  'periodicity_minute',
  'periodicity_minute_frequency',
  'periodicity_month',
  'periodicity_month_day',
  'periodicity_month_frequency',
  'periodicity_start_date',
  'periodicity_stop_date',
  'periodicity_week',
  'periodicity_week_day',
  'periodicity_week_frequency',
]
result_list = ['Alarm;Enabled;ReportMethodId;ActiveSenseMethodId;SenseMethodId;SolveMethodId;' + ';'.join(periodicity_list)]
for alarm in alarm_tool.contentValues():
  in_list = [
    alarm.getRelativeUrl(),
    str(alarm.getEnabled()),
    str(alarm.getReportMethodId()),
    str(alarm.getActiveSenseMethodId()),
    str(alarm.getSenseMethodId()),
    str(alarm.getSolveMethodId())
  ]
  for periodicity_id in periodicity_list:
    in_list.append(str(getattr(alarm, periodicity_id, None)))
  result_list.append(';'.join(in_list))
result_list.sort()
return '\n'.join(result_list)
