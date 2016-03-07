kw.setdefault("portal_type",context.getPortalCalendarPeriodTypeList())
return context.portal_simulation.getAvailableTimeMovementList(
  node_uid=[context.getUid()],
  from_date=from_date,
  to_date=to_date,
  **kw)
