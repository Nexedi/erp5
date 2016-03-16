"""
  Run upgrader
"""
portal = context.getPortalObject()
portal_alarms = portal.portal_alarms

after_method_id = 'Base_postCheckConsistencyResult'
def launchSenseAlarm(alarm_id, after_tag=[]):
  """ Get the alarm and use sense"""
  upgrader_alarm = getattr(portal_alarms, alarm_id, None)
  if upgrader_alarm is not None:
    # call solve method
    kw = {"tag": alarm_id,
      "after_method_id": after_method_id}
    if len(after_tag) > 0:
      kw["after_tag"] = after_tag
    method_id = upgrader_alarm.getActiveSenseMethodId()
    if method_id not in (None, ''):
      method = getattr(upgrader_alarm.activate(**kw), method_id)
      method()
    return [alarm_id,]
  return after_tag

previous_tag = launchSenseAlarm('upgrader_check_pre_upgrade')

previous_tag = launchSenseAlarm('upgrader_check_upgrader',
                                   after_tag=previous_tag)

previous_tag = launchSenseAlarm('upgrader_check_post_upgrade',
                 after_tag=previous_tag)

active_process = context.newActiveProcess()
context.activate(after_tag=previous_tag,
  after_method_id=after_method_id).Alarm_postFullUpgradeNeed(
  active_process=active_process.getRelativeUrl())
