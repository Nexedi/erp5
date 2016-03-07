"""
Update from time to time all time table lines to set end periodicity at
end of following month
"""
now = context.Base_getNowDate().earliestTime()
first_day_month_quantity = 0
date_cursor = now
while True:
  if date_cursor.dd() == "01":
    first_day_month_quantity += 1
  if first_day_month_quantity == 13:
    break
  date_cursor += 1
portal = context.getPortalObject()
for time_table_line in portal.portal_catalog(portal_type="Time Table Line",
                                             validation_state="!= invalidated"):
  time_table_line.edit(periodicity_stop_date=date_cursor)
# Now reindex all Group Calendar Assignment to take into account new changes
portal.portal_catalog.searchAndActivate(
    method_id="reindexObject",
    activate_kw={"priority": 5},
    simulation_state="!=cancelled AND !=draft",
    portal_type="Group Calendar Assignment")
