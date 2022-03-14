from builtins import str
Base_translateString = context.Base_translateString

if not context.getReference() or force:
  if not employee_number:
    employee_number = str(context.portal_ids.generateNewId(id_group='employee_number', id_generator='uid')).zfill(8)
  context.edit(reference=employee_number)
  if not batch:
    return context.Base_redirect('view', keep_items={
      'portal_status_message': Base_translateString('Employee Number: ${employee_number} is set',
                                                    mapping=dict(employee_number=employee_number))})
else:
  return context.Base_redirect('view', keep_items={
    'portal_status_message': Base_translateString('User has already Employee Number'),
    'portal_status_level': 'error'
  })
