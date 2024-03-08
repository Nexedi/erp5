leave_request = context.getCausalityRelatedValue(portal_type='Leave Request')
# I think I dont need this.
if leave_request:
  return leave_request.Base_redirect('view', context.Base_translateString('Leave Request is already created'))

raise NotImplementedError

#employee = context.getSourceSectionValue()
#stop_date = context.getStopDate()


#holiday_acquisition = context.holiday_acquisition_module.newContent(
#  portal_type="Holiday Acquisition",
#  quantity = holiday_per_hour * work_hour,
#  start_date= stop_date,
#  stop_date =  stop_date,
#  title= "Holiday %s For %s " % (stop_date.strftime('%Y%m'), employee.getTitle()),
#  destination_value = employee,
#  resource = resource,
#  causality = context.getRelativeUrl()
#)
#
#holiday_acquisition.plan()
#return holiday_acquisition.Base_redirect('view',
#  context.Base_translateString('Holiday Acquisition is created'))
