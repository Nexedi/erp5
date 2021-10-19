registration_number = str(context.portal_ids.generateNewId(id_group='registration_number', id_generator='uid')).zfill(8)
context.edit(registration_number = registration_number)
if not batch:
  return context.Base_redirect('Person_viewDetails', keep_items={'portal_status_message': 'Registration Number: %s is set' % registration_number})
