"""
This script collects *all* filled properties in the M0
request_eform and creates a new Organisation record.
"""

# Initalize some useful variables
person_module = context.getPortalObject().person_module
request_eform = sci['object']
duration = request_eform.getDuration()
duration_length =int(duration.split(' ').pop(0))
beginning_date = request_eform.getBeginningDate()
y = beginning_date.year()
m = beginning_date.month()
d = beginning_date.day()
stop_year = y+duration_length
first_associate= person_module.newContent(portal_type ='Person')
first_associate_assignment = first_associate.newContent(portal_type ='Assignment',
  function = 'entreprise/associe',
  start_date =organisation.getStartDate(),
  stop_date ="%04d/%02d/%02d" % (stop_year, m, d),
  destination_value = organisation,
)
#Second Associate
second_associate= person_module.newContent(portal_type ='Person')
second_associate.edit(
  last_name =request_eform.getSecondAssociateLastname(),
  first_name = request_eform.getSecondAssociateFirstname(),
  start_date = request_eform.getSecondAssociateBirthday(),
  career_subordination_value = organisation,
)
second_associate_assignment = second_associate.newContent(portal_type ='Assignment',
  function = 'entreprise/associe',
  start_date =organisation.getStartDate(),
  stop_date=organisation.getStopDate(),
  destination_value = organisation,
)
