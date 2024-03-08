leave_request_list = context.PaySheetTransaction_getRelatedLeaveRequestList()
message = context.Base_translateString('Leave Request related:')
if leave_request_list and len(leave_request_list) == 1:
  return leave_request_list[0].Base_redirect('view', keep_items={
    'portal_status_message': message})

if leave_request_list and len(leave_request_list) > 1:
  # Redirect to module
  redirect_context = context.getPortalObject().leave_request_module
  return redirect_context.Base_redirect('view', keep_items={
    'portal_status_message': message,
    # We expect that the number is small since there are only 31 possible
    # days to take a leave.
    'reset': 1,
    'ignore_hide_rows': 1,
    'uid': [i.uid for i in leave_request_list]})

return context.Base_redirect('view', keep_items={'portal_status_message': \
      context.Base_translateString('Leave Request not found.')})
