# Returns an ID internal to each DSN Report, referencing to an insurance contract.
# This Script is meant to be overidden in project configuration, depending
# of the insurance contracts made by the company.
# Default Values here are set only for a purpose of testing.

registration_code = context.getSourceSectionValue().getCorporateRegistrationCode()

if registration_code == 'ORGANISATION1':
  return '1'
elif registration_code == 'ORGANISATION2':
  return '2'
else:
  return ''
