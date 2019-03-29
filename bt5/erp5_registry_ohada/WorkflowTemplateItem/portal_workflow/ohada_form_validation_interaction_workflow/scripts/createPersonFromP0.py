"""This script collects *all* filled properties in the P0
request_eform and creates a new Person record and an organisation for this person.
"""

# Initalize some useful variables
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
from Products.DCWorkflow.DCWorkflow import ValidationFailed

request_eform = state_change['object']
portal = request_eform.getPortalObject()
person_module = portal.person_module
organisation_module = portal.organisation_module
organisation = None
if not request_eform.getActivityRestartCheck():
  organisation = organisation_module.newContent(portal_type='Organisation')
  organisation.edit(title = request_eform.getLogo(),
                    corporate_name = request_eform.getLogo(),
                    activity_free_text = request_eform.getMainActivityFreeText(),
                    default_address_street_address = request_eform.getRealAddress())
else:
  rccm = request_eform.getPreviousActivityCorporateRegistrationCode()
  if rccm :
    organisation_list = portal.organisation_module.searchFolder(\
        corporate_registration_code=rccm)
    if len(organisation_list) >1 :
      raise ValidationFailed("Error : There is more than one organisation with the "\
              " rccm number '%s'" % rccm)
    elif len(organisation_list) == 0:
      raise ValidationFailed("Error : There is no organisation with the "\
              " rccm number '%s'" % rccm)
    organisation = organisation_list[0].getObject()

if request_eform.getBeginning():
  organisation.setRole('commerce/siege')
if request_eform.getOpening():
  organisation.setRole('commerce/succursale')

date = request_eform.getDate()
# Create a new person based on eform data
# we suppose here that all data in the form has
# been validated - ex. by a constraint on the
# validate transition or by any guard script
request_eform.setTitle(request_eform.getFirstName() + ' ' + request_eform.getLastName())
#Custom method used to create custom-made corporate_registration_codes for the companies
def attachLocationYearInfo(last_id):
  location_info = request_eform.getSite().split('/')[0]
  if location_info == 'dakar':
    location_initials = 'DKR'
  elif location_info == 'thies':
    location_initials = 'TH'
  elif location_info == 'saint-louis':
    location_initials = 'SL'
  year = str(date.year())
  type_of_form = 'A'
  attach_info = 'SN' + location_initials + year + type_of_form
  last_corporate_registration_code = str(str(last_id).split('-').pop())
  new_corporate_registration_code  = '%05d' % int(str(int(last_corporate_registration_code)+1))
  return ('-'.join(['SN', location_initials, year, type_of_form, new_corporate_registration_code]))

# We shall now allocate a new registry number
# using the custom method attachLocationYearInfo
# we use corporate_registry for corporations and
# merchant_registry for merchants.
# the id_group is extended with the group path so that
# each local registry has a different sequence

group = (date.year(),)

new_registry_number = request_eform.portal_ids.generateNewId(
                                     id_group = group,
                                     method = attachLocationYearInfo)

# build a query and search in person module if the person already exists,
# if the person does not exist, create the person and a new assignment for 
# the person with function commercant on the organisation if the 
# person exist, just add a new assignment for the person with the function
# commercant on organisation
query=ComplexQuery(Query(title=request_eform.getTitle()),
             Query(birth_date=request_eform.getStartDate()),
             Query(birthplace_city=request_eform.getDefaultBirthplaceAddressCity()),
             logical_operator="AND")
person_list = [person.getObject() for person in person_module.searchFolder(query=query)]
if  request_eform.getBeginning() or request_eform.getOpening():
  if len(person_list) == 0:
    person = person_module.newContent(portal_type='Person')
    person.edit(
      first_name = request_eform.getFirstName(),
      last_name = request_eform.getLastName(),
      default_address_street_address = request_eform.getHeadOfficeAddress(),
      start_date = request_eform.getStartDate(),
      default_birthplace_address_city = request_eform.getDefaultBirthplaceAddressCity(),
      default_address_city = request_eform.getPlace(),
      nationality = request_eform.getCitizenship().lower())
    # Update matrimonial situation for the person
    if request_eform.getMarriedCheck():
      person.edit(marital_status = 'married')
    elif request_eform.getDivorcedCheck():
      person.edit(marital_status = 'divorced')
    elif request_eform.getSingleCheck():
      person.edit(marital_status = 'single')
    elif request_eform.getWidowerCheck():
      person.edit(marital_status = 'widowed')
    if request_eform.getMrCheck():
      person.edit(gender = 'male')
    else:
      person.edit(gender = 'female')

  else: # person exists
    if len(person_list) >1 :
      raise ValidationFailed("Error : There is more than one person with the "\
              " title '%s', birth date '%s' and birthplace '%s'" % (request_eform.getTitle(),
                  request_eform.getStartDate(),
                  request_eform.getDefaultBirthplaceAddressCity()))
    elif len(person_list) == 0:
      raise ValidationFailed("Error : There is nobody with the "\
              " title '%s', birth date '%s' and birthplace '%s'" % (request_eform.getTitle(),
                  request_eform.getStartDate(),
                  request_eform.getDefaultBirthplaceAddressCity()))
    else:
      person = person_list[0]

  # add a new assignment to this person and open existing assignments
  destination_form_uid = context.portal_categories.destination_form.getUid()
  assignment_list = [assignment.getObject() for assignment in context.portal_catalog(portal_type='Assignment',
                      validation_state = 'open_submitted',
                      destination_form_uid = request_eform.getUid())]
  for assignment in assignment_list:
    assignment.open()
    assignment.edit(destination_value=organisation,
                   corporate_registration_code=new_registry_number)
  assignment = person.newContent(portal_type='Assignment',
                                 function='commerce/commercant',
                                 start_date=request_eform.getBeginningDate(),	
                                 destination_form_value=request_eform,
                                 destination_value=organisation)
  assignment.openSubmit()
  assignment.open()
  person.updateLocalRolesOnSecurityGroups()

# In case of an harmonisation, update the organisation corporate_registration_code with the old corporate_registration_code
#used to create the organisation
if not request_eform.getBeginning() and not request_eform.getActivityRestartCheck() and not request_eform.getOpening():
  organisation.edit(corporate_registration_code = request_eform.getCorporateRegistrationCode(),
    geographic_incorporate_code = '-'.join(str(request_eform.getCorporateRegistrationCode()).split('-')[0:2])
)
elif not request_eform.getActivityRestartCheck():
  organisation.edit(corporate_registration_code = new_registry_number,
    geographic_incorporate_code = '-'.join(str(new_registry_number).split('-')[0:2])
  )

# In case of opening a secondary establishment, the main company rccm number
# have to be saved in source_reference variable 
if request_eform.getOpening():
  organisation.setSourceReference(request_eform.getPreviousOwnerCorporateRegistrationCode())

organisation.activerEntreprise()
organisation.updateLocalRolesOnSecurityGroups()
# Update the request_eform with the allocated number
request_eform.edit(corporate_registration_code = new_registry_number,
                   registration_number = new_registry_number)
# Update the registration date of the request_eform with the time when the registry officer
#validates the transition
history_list = request_eform.portal_workflow.getInfoFor(request_eform,
                                                        'history',
                                                        wf_id='egov_form_validation_workflow')
for history in history_list:
  if history['action'] == 'validate_action':
    request_eform.edit(registration_date = history['time'])
