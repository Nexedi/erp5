if REQUEST is not None:
  from zExceptions import Unauthorized
  raise Unauthorized("You can not call this script from the url")

alarm_id_list = ("upgrader_check_pre_upgrade",
  "upgrader_check_upgrader",
  "upgrader_check_post_upgrade")

portal = context.getPortalObject()
portal_alarms = portal.portal_alarms
message_list = []

for alarm_id in alarm_id_list:
  alarm = getattr(portal_alarms, alarm_id, None)
  if alarm is not None and alarm.sense():
    last_active_process = alarm.getLastActiveProcess()
    result_list = last_active_process.getResultList()
    if result_list:
      detail = result_list[0].detail
    else:
      detail = ["Require solve %s" % alarm_id,]
    message_list.extend(detail)

active_process = portal.restrictedTraverse(active_process)
if message_list:
  active_process.postActiveResult(
    summary=context.getTitle(),
    severity=1, detail=message_list)
