alarm = context

if (params is None) or (not params.get('Base_reindexAndSenseAlarm', False)):
  # if not called by Base_reindexAndSenseAlarm
  # do nothing, as only Base_reindexAndSenseAlarm will ensure searched document are indexed
  # before alarm call
  return None

active_process = alarm.getLastActiveProcess(include_active=1)
if active_process is None:
  previous_run_date = None
  active_process = alarm.newActiveProcess()
else:
  previous_run_date = active_process.getStartDate()

active_process.edit(start_date=DateTime())
return previous_run_date
