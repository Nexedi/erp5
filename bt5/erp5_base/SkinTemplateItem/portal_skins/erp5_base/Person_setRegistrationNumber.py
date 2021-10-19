number = str(context.portal_ids.generateNewId(id_group='employee_registration_number', id_generator='uid')).zfill(8)
employee_registration_number = getattr(context, 'employee_registration_number', None)
if not employee_registration_number:
  employee_registration_number = context.newContent(
    portal_type='External Identifier',
    id='employee_registration_number'
  )
employee_registration_number.edit(
  coordinate_text = number,
  title='Employee registration number'
)
if not batch:
  return context.Base_redirect('view', keep_items={'portal_status_message': 'Registration Number: %s is set' % number})
