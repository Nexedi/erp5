"""
This script is used to create links between these forms and the correponding organisations
or persons
"""
# Initalize some useful variables
request_eform = state_change['object']
portal =request_eform.getPortalObject()
application_date = request_eform.getDate()

#Custom method used to create custom-made corporate_registration_codes for the companies
def attachLocationYearInfo(last_id):
  location_info = request_eform.getSite().split('/')[0]
  if location_info == 'dakar':
    location_initials = 'DKR'
  elif location_info == 'thies':
    location_initials = 'TH'
  elif location_info == 'saint-louis':
    location_initials = 'SL'
  year = str(application_date.year())
  type_of_form = 'S'
  attach_info = 'SN' + location_initials + year + type_of_form
  last_corporate_registration_code = str(str(last_id).split('-').pop())
  new_corporate_registration_code  = '%05d' % int(str(int(last_corporate_registration_code)+1))
  return ('-'.join(['SN', location_initials, year, type_of_form,new_corporate_registration_code]))

# We shall now allocate a new registry number
# using the custom method attachLocationYearInfo
# we use corporate_registry for corporations and
# merchant_registry for merchants.
# the id_group is extended with the group path so that
# each local registry has a different sequence
default_address_city = request_eform.getPlace()

group = (application_date.year(),)
new_registry_number = request_eform.portal_ids.generateNewId(
                                     id_group = group,
                                     method = attachLocationYearInfo)


# Update the request_eform with the allocated number
request_eform.edit(registration_number=new_registry_number)
# Update the registration date of the request_eform with the time when the registry officer
#validates the transition
history_list = request_eform.portal_workflow.getInfoFor(request_eform, 'history', wf_id='egov_form_validation_workflow')
for history in history_list:
  if history['action'] == 'validate_action':
    request_eform.edit(registration_date=history['time'],
                       second_registration_date=history['time'])
