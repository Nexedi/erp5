state_change['object'].localBuild()
alarm = getattr(state_change.getPortal().portal_alarms, "invoice_builder_alarm",
  None)
if alarm is not None:
  alarm.activeSense()
