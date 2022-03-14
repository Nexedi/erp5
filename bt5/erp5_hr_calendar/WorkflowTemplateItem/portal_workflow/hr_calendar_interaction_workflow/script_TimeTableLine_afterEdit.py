# A Time Table Line is a generic Presence Period with some UI simplification.
# In the UI, only day of week and quantity is defined. Therefore we will
# automatically set a good start and stop date to make generic code working

from DateTime import DateTime
from erp5.component.module.DateUtils import addToDate
time_table_line = state_change["object"]

day_of_week = time_table_line.getDayOfWeek()
quantity = time_table_line.getQuantity()
if not(None in (day_of_week, quantity)):
  time_table_line.setPeriodicityWeekDayList([day_of_week])
  start_date = time_table_line.getParentValue().getStartDate(DateTime("2014/04/01"))
  while start_date.Day() != day_of_week:
    start_date = addToDate(start_date, day=1)
  time_table_line.setStartDate(start_date)
  stop_date = addToDate(start_date, hour=quantity)
  time_table_line.setStopDate(stop_date)
# after change, make sure to update group calendars through the usual alarm
context.getPortalObject().portal_alarms.update_time_table_end_periodicity.activate(
  priority=5).activeSense()
