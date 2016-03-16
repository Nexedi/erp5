alarm_tool = context.getPortalObject().portal_alarms
kw["id"] = "promise_%"

alarm_list = []
for alarm in alarm_tool.searchFolder(**kw):
  alarm.activeSense()
  if alarm.sense():
    alarm_list.append(alarm)

return alarm_list
