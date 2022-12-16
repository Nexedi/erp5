ticket = state_change["object"]
portal = context.getPortalObject()

portal_type = ticket.getPortalType()
if portal_type in ("Leave Request", "Leave Request Period"):
  container.script_Alarm_safeTrigger(
    portal.portal_alarms.create_representative_record_for_leave_request
  )
elif portal_type in ("Expense Validation Request"):
  container.script_Alarm_safeTrigger(
    portal.portal_alarms.create_representative_record_for_expense_validation_request
  )
elif portal_type in ("Travel Request"):
  container.script_Alarm_safeTrigger(
    portal.portal_alarms.create_representative_record_for_travel_request
  )
