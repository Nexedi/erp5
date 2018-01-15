assert context.getPortalType() == "Group Calendar Assignment"
portal = context.getPortalObject()
period_list = []
# look when we workers should be available with time tables
group_calendar = context.getSpecialiseValue()
if group_calendar is not None:
  period_dict = {}
  for period in group_calendar.objectValues(portal_type=portal.getPortalCalendarPeriodTypeList()):
    period_list.append(period)
    period_dict[period.getStartDate().Day()] = period.getQuantity()
  # And then we subscract not working days
  start_date = context.getStartDate()
  if start_date is not None:
    stop_date = context.getStopDate()
    if stop_date is None:
      # We assume that there is a periodicity_stop_date correctly define on time table line
      assert len(period_list) > 0 # this should be always the case in Woelfel
      stop_date = period_list[0].getPeriodicityStopDate()
    if stop_date is not None:
      region_uid = group_calendar.getRegionUid()
      if region_uid:
        # Get all public holidays containers matching the right country
        catalog_kw = {}
        for public_holiday in portal.portal_catalog(portal_type="Public Holiday Line",
                          parent_region_uid=region_uid, validation_state="validated", **catalog_kw):
          public_holiday = public_holiday.getObject()
          if public_holiday.getStartDate() >= start_date and public_holiday.getStopDate() < stop_date:
            quantity = - period_dict[public_holiday.getStartDate().Day()] * (1 - public_holiday.getQuantity())
            if quantity:
              period_list.append(public_holiday.asContext(quantity=quantity, stop_date=public_holiday.getStartDate()+1))
return period_list
