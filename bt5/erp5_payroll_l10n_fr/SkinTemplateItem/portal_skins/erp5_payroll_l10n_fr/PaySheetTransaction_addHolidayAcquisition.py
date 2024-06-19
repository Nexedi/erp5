holiday_acquisition = context.getCausalityRelatedValue(portal_type='Holiday Acquisition')
if holiday_acquisition:
  return holiday_acquisition.Base_redirect('view', 
    keep_items={
      'portal_status_message': 
        context.Base_translateString('Holiday Acquisition is already created')})

employee = context.getSourceSectionValue()
stop_date = context.getStopDate()

holiday_per_hour = float(25)/12/151.67
work_hour = context.getWorkTimeAnnotationLineQuantity(0)

if work_hour is None:
  return context.Base_redirect('view',
    keep_items={
      'portal_status_message': 
        context.Base_translateString(
          'Cannot create a Holiday Acquisition without set work time.')})

holiday_acquisition = context.holiday_acquisition_module.newContent(
  portal_type="Holiday Acquisition",
  quantity = holiday_per_hour * work_hour,
  start_date= stop_date,
  stop_date =  stop_date,
  title= "Holiday %s For %s " % (stop_date.strftime('%Y%m'), employee.getTitle()),
  destination_value = employee,
  resource = resource,
  causality = context.getRelativeUrl()
)

holiday_acquisition.plan()
return holiday_acquisition.Base_redirect('view',
  keep_items={
    'portal_status_message': 
      context.Base_translateString('Holiday Acquisition is created')})
