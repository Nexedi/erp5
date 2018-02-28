from Products.ERP5Type.DateUtils import addToDate

supply = context
time_quantity_unit_value = supply.getTimeQuantityUnitValue()

if time_quantity_unit_value is None:
  return

time_second_ratio = float(context.getPortalObject().portal_categories.quantity_unit.time.second.getProperty('quantity'))

time_second_conversion_ratio = float(time_quantity_unit_value.getProperty('quantity')) / time_second_ratio

if use_min_delay:
  delay_second = supply.getMinDelay() * time_second_conversion_ratio
  order_delay_second = supply.getMinOrderDelay() * time_second_conversion_ratio
else:
  delay_second = supply.getMaxDelay() * time_second_conversion_ratio
  order_delay_second = supply.getMaxOrderDelay() * time_second_conversion_ratio

if effective_date is not None:
  start_date = addToDate(effective_date, second=order_delay_second)
  stop_date = addToDate(start_date, second=delay_second)
elif start_date is not None:
  effective_date = addToDate(start_date, second=-order_delay_second)
  stop_date = addToDate(start_date, second=delay_second)
elif stop_date is not None:
  start_date = addToDate(stop_date, second=-delay_second)
  effective_date = addToDate(start_date, second=-order_delay_second)
else:
  effective_date = DateTime().earliestTime()
  start_date = addToDate(effective_date, second=order_delay_second)
  stop_date = addToDate(start_date, second=delay_second)

return effective_date, start_date, stop_date
