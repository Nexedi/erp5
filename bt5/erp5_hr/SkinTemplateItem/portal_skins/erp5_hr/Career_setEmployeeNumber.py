if not context.getReference() or force:
  if not employee_number:
    employee_number = str(context.portal_ids.generateNewId(id_group='employee_number', id_generator='uid')).zfill(8)
  context.edit(reference=employee_number)
  if not batch:
    return context.Base_redirect('view', keep_items={'portal_status_message': 'Employee Number: %s is set' % employee_number})
else:
  return context.Base_redirect('view', keep_items={'portal_status_message': 'User has already Employee Number'})
