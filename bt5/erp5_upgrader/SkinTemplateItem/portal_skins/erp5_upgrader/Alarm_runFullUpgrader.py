"""
  Run upgrader
"""
portal = context.getPortalObject()
portal_alarms = portal.portal_alarms

def launchUpgraderAlarm(alarm_id, after_tag=None):
  """ Get the alarm and use sense and solve """
  if after_tag is None:
    after_tag = []
  upgrader_alarm = getattr(portal_alarms, alarm_id, None)
  if upgrader_alarm is not None and (force or upgrader_alarm.sense()):
    # call solve method
    tag = alarm_id
    activate_kw = dict(tag=tag)
    activate_kw["after_tag"] = after_tag
    method_id = upgrader_alarm.getSolveMethodId()
    if method_id not in (None, ''):
      method = getattr(upgrader_alarm.activate(**activate_kw), method_id)
      method(force=force, activate_kw=activate_kw)
    return [tag] + after_tag
  return after_tag

previous_tag = launchUpgraderAlarm('upgrader_check_pre_upgrade')

previous_tag = launchUpgraderAlarm('upgrader_check_upgrader',
                                   after_tag=previous_tag)

previous_tag = launchUpgraderAlarm('upgrader_check_post_upgrade',
                                   after_tag=previous_tag)

# Nothing else to do, so we can disable.
context.setEnabled(False)
return
