registration_number = getattr(context, 'employee_registration_number', None)
if registration_number:
  return registration_number.getCoordinateText()
return ''
