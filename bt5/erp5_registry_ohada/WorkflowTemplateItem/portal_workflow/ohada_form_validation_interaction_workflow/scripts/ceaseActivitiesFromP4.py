"""
This script collects properties in the P4
request_eform and use them to either stop temporarely or definitively activities for the organisations of the physical person.
"""

from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
#Initialize some useful variables
request_eform = state_change['object']
portal = request_eform.getPortalObject()
rccm = request_eform.getCorporateRegistrationCode()
application_date = request_eform.getDate()
request_eform.setTitle(request_eform.getOwnerFirstName()+' '+request_eform.getOwnerLastName())

organisation_list = [organisation.getObject() for organisation in \
     portal.organisation_module.searchFolder(corporate_registration_code=rccm)]
context.log(organisation_list)
for organisation in organisation_list:
  if request_eform.getDefinitiveCheck():
    organisation.edit(stop_date = request_eform.getSecondDate())
    organisation.mettreEntrepriseEnCessation()
    organisation.liquiderEntreprise()
    organisation.radierEntreprise()
  elif request_eform.getTemporaryCheck():
    organisation.edit(stop_date = request_eform.getStopTemporaryActivityDate())
    organisation.stopActivities()

def attachLocationYearInfo(last_id):
  location_info = request_eform.getSite().split('/')[0]
  if location_info == 'dakar':
    location_initials = 'DKR'
  elif location_info == 'Thies':
    location_initials = 'TH'
  elif location_info == 'Saint-Louis':
    location_initials = 'SL'
  year = str(application_date.year())
  type_of_form = 'M'
  attach_info = 'SN' + location_initials + year + type_of_form
  last_corporate_registration_code = str(str(last_id).split('-').pop())
  new_corporate_registration_code  = '%05d' % int(str(int(last_corporate_registration_code)+1))
  return ('-'.join(['SN', location_initials, year,
          type_of_form, new_corporate_registration_code]))

# We shall now allocate a new registry number
# using the custom method attachLocationYearInfo
# we use corporate_registry for corporations and
# merchant_registry for merchants.
# the id_group is extended with the group path so that
# each local registry has a different sequence
group = (application_date.year(),)

new_registry_number = request_eform.portal_ids.generateNewId(
                                     id_group = group,
                                     method = attachLocationYearInfo)

# Update the request_eform with the allocated number
request_eform.edit(registration_number = new_registry_number)
# Update the registration date of the request_eform with the time when the registry officer
#validates the transition
history_list = context.portal_workflow.getInfoFor(request_eform,
                                                  'history',
                                                   wf_id='egov_form_validation_workflow')
for history in history_list:
  if history['action'] == 'validate_action':
    request_eform.edit(registration_date=history['time'])
