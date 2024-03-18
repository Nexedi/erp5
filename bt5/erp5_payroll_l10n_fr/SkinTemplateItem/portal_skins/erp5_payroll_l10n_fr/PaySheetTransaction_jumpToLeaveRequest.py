leave_request_list = None # TODO

if leave_request_list and len(leave_request_list) == 1:
  message = context.Base_translateString('Leave Request is already created')
  return leave_request_list[0].Base_redirect('view', keep_items={
    'portal_status_message': message})

if leave_request_list and len(leave_request_list) > 1:
  message = context.Base_translateString('Leave Request is already created')
  # Redirect to module
  return leave_request_list.Base_redirect('view', keep_items={
    'portal_status_message': message})

return context.Base_redirect('view',keep_items={'portal_status_message': \
      context.Base_translateString('Leave Request not found')})
