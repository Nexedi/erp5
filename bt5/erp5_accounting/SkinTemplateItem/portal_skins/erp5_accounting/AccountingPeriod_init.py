from DateTime import DateTime

period_list = context.getParentValue().searchFolder(
           simulation_state=['started', 'confirmed', 'delivered'],
           sort_on=[('delivery.stop_date', 'ASC'),] )

if period_list:
  last_period  = period_list[-1].getObject()
  new_date = last_period.getStopDate() + 1
  context.setStartDate(new_date)
  context.setStopDate(DateTime(new_date.year(), 12, 31))
