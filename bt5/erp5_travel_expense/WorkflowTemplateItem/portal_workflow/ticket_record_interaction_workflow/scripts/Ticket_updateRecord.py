ticket = state_change["object"]
portal = context.getPortalObject()

portal_type = ticket.getPortalType()
if portal_type in ("Leave Request", "Leave Request Period"):
  context.Alarm_safeTrigger(
    portal.portal_alarms.create_representative_record_for_leave_request
  )
elif portal_type in ("Expense Validation Request"):
  context.Alarm_safeTrigger(
    portal.portal_alarms.create_representative_record_for_expense_validation_request
  )
elif portal_type in ("Travel Request"):
  context.Alarm_safeTrigger(
    portal.portal_alarms.create_representative_record_for_travel_request
  )
