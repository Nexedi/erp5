# When updating public holidays, we have to recatalog group calendar
# assignments since they could be affected

from DateTime import DateTime
public_holiday_line = state_change["object"]

if public_holiday_line.getValidationState() == "validated":
  start_date = public_holiday_line.getStartDate()
  quantity = public_holiday_line.getQuantity()
  if not(None in (start_date, quantity)):
    context.getPortalObject().portal_alarms.update_time_table_end_periodicity.activate(priority=5).activeSense()
