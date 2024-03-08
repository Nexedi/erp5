leave_request_list = context.PaySheetTransaction_getRelatedLeaveRequestList()
# I think I dont need this.
if leave_request_list:
  return context.Base_redirect('view',
    keep_items={
      'portal_status_message': context.Base_translateString(
        'You have at least one Leave Period for the period.')})

employee = context.getSourceSectionValue()
stop_date = context.getStopDate()

if not stop_date or not context.getStartDate():
  return context.Base_redirect('view',
    keep_items={
      'portal_status_message': context.Base_translateString(
        'Please set Start Date and Stop Date.')})

leave_request = context.leave_request_module.newContent(
  portal_type="Leave Request",
  start_date=context.getStartDate(),
  stop_date=stop_date,
  title="Leave Request %s For %s " % (stop_date.strftime('%Y%m'), employee.getTitle()),
  destination_value = employee,
  resource = resource,
)

# Create a period
leave_request.newContent(
  portal_type="Leave Request Period",
  start_date=leave_request.getStartDate(),
  stop_date=leave_request.getStopDate(),
  resource=leave_request.getResource(),
  quantity=quantity
)

return leave_request.Base_redirect('view',
  keep_items={
    'portal_status_message': 
      context.Base_translateString('Leave Request is created')})
