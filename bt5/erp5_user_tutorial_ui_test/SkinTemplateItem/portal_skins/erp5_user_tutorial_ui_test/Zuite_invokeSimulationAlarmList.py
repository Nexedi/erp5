alarm_id_list = ['packing_list_builder_alarm',
                 'invoice_builder_alarm']

for alarm_id in alarm_id_list:
  alarm = getattr(context.portal_alarms, alarm_id, None)
  if alarm is not None:
    alarm.activeSense()
  elif strict:
    raise ValueError("Alarm %s not found" % alarm_id)

return "Done."
