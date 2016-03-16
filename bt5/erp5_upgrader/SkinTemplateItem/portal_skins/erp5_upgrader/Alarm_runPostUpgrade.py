"""
  Run Post upgrade
"""
portal_alarms = context.getPortalObject().portal_alarms
active_process = context.newActiveProcess()

# We should not run post upgrade if upgrader was not solved or never executed
alarm = getattr(portal_alarms, 'upgrader_check_upgrader')
if not(force) and alarm.sense() in (None, True):
  active_process.postActiveResult(summary=context.getTitle(),
      severity=1,
      detail=["Is required run upgrade before solve it. You need run active sense once at least on this alarm"])
  return

context.ERP5Site_checkUpgraderConsistency(fixit=True,
  activate_kw=activate_kw,
  active_process=active_process,
  filter_dict={"constraint_type": "post_upgrade"})

context.setEnabled(False)
return
