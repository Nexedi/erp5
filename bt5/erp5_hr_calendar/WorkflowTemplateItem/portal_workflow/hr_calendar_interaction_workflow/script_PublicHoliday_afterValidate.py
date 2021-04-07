# When updating public holidays, we have to recatalog group calendar
# assignments since they could be affected
context.getPortalObject().portal_alarms.update_time_table_end_periodicity.activate(priority=5).activeSense()
