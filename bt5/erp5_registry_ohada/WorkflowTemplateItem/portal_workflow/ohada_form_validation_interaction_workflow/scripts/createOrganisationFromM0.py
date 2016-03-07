"""
This script collects *all* filled properties in the M0
request_eform and creates a new Organisation record.
"""

# Initalize some useful variables

request_eform = state_change['object']
portal = request_eform.getPortalObject()
organisation_module = portal.organisation_module
date = request_eform.getDate()
# get duration length of the company
duration = request_eform.getDuration()
duration_length = int(duration.split(' ').pop(0))
beginning_date = request_eform.getBeginningDate()
year = beginning_date.year()
month = beginning_date.month()
day = beginning_date.day()
stop_year = year + duration_length
# Create a new organisation based on eform data
# we suppose here that all data in the form has
# been validated - ex. by a constraint on the
# validate transition or by any guard script
organisation = organisation_module.newContent(portal_type='Organisation')
organisation.edit(
  title=request_eform.getTitle(),
  corporate_name=request_eform.getName(),
  acronym=request_eform.getInitials(),
  sign=request_eform.getSign(),
  default_address_city=request_eform.getDefaultAddressCity(),
  social_form='%s' % request_eform.getLegalForm().lower(),
  price_currency='currency_module/1', # object 1 is the devise XOF
  site='dakar/pikine_guediawaye/tribunal', #XXX this should not be hardcoded
  start_date=request_eform.getBeginningDate(),
  stop_date="%04d/%02d/%02d" % (stop_year, month, day),
  social_capital=request_eform.getCapital(),
  creation=request_eform.getCreationCheck(),
  purchase=request_eform.getPurchaseCheck(),
  contribution=request_eform.getContributionCheck(),
  other=request_eform.getOtherCheck(),
  other_reason=request_eform.getOtherCheckInfo(),
)
# if activity field on M0 too small, get activity from M0 bis
M0_bis_list = [x.getObject() for x in request_eform.contentValues(portal_type='M0 Bis')]
if len(M0_bis_list) and request_eform.getActivityCheck():
  m0_bis_activity_list = [m0_bis.getM0BisActivityFreeText() for m0_bis in M0_bis_list]
  m0_bis_activities = ','.join(m0_bis_activity_list)
  organisation.edit(activity_free_text=','.join((request_eform.getActivityFreeText(), m0_bis_activities)))
else:
  organisation.edit(activity_free_text=request_eform.getActivityFreeText())

# Custom method used to create custom-made corporate_registration_code for the companies
def attachLocationYearInfo(last_id):
  location_info = request_eform.getSite().split('/')[0]
  if location_info == 'dakar':
    location_initials = 'DKR'
  elif location_info == 'thies':
    location_initials = 'TH'
  elif location_info == 'saint-louis':
    location_initials = 'SL'
  year = str(date.year())
  if request_eform.getMoralPerson():
    if request_eform.getLegalForm() and request_eform.getLegalForm().lower() == 'gie':
      type_of_form ='C'
    else:
      type_of_form = 'B'
  elif request_eform.getSecondCompany():
    type_of_form = 'M'
  elif request_eform.getBranch():
    type_of_form = 'E'
  else:
    type_of_form = 'M'
  last_corporate_registration_code = str(str(last_id).split('-').pop())
  new_corporate_registration_code  = '%05d' % int(str(int(last_corporate_registration_code)+1))
  return ('-'.join(['SN', location_initials, year,
    type_of_form,new_corporate_registration_code]))
  
# We shall now allocate a new registry number
# using custom method attachLocationYearInfo
# we use corporate_registry for corporations and
# merchant_registry for merchants.
# the id_group is extended with the group path so that
# each local registry has a different sequence
default_address_city = request_eform.getDefaultAddressCity()

group = (date.year(),)
#id_group ='sn-%s-%s'%(str(date.year()),request_eform.getGroup())
new_registry_number = request_eform.portal_ids.generateNewId(
                                     id_group = group,
                                     method = attachLocationYearInfo)


# Open all assignemnts that are in open_submitted state
person_module = context.getPortalObject().person_module
destination_form_uid = context.portal_categories.destination_form.getUid()
assignment_list = [assignment.getObject() for assignment in context.portal_catalog(portal_type='Assignment',
                      validation_state = 'open_submitted',
                      destination_form_uid = request_eform.getUid())]
for assignment in assignment_list:
  assignment.open()
  assignment.edit(destination_value=organisation,
                   corporate_registration_code=new_registry_number)

# Changes roles when secondaries organisations are created and update the organisation with
# the corresponding corporate_registration_code number
if request_eform.getMoralPerson():
  organisation.edit(role='entreprise/siege',
                   corporate_registration_code=new_registry_number,
                   source_reference=new_registry_number,
                   default_address_street_address=request_eform.getHeadOfficeAddress(),
  geographic_incorporate_code ='-'.join(str(new_registry_number).split('-')[0:2]))
  request_eform.edit(corporate_registration_code = new_registry_number)
elif request_eform.getBranch():
  organisation.edit(role='entreprise/succursale',
                  default_address_street_address=request_eform.getFirstCompanyAddress(),
                  corporate_registration_code = new_registry_number,
                  source_reference=request_eform.getCorporateRegistrationCode())
elif request_eform.getSecondCompany():
  organisation.edit(role = 'entreprise/agence',
                    default_address_street_address=request_eform.getWorkAddress(),
                    corporate_registration_code = new_registry_number,
                    source_reference=request_eform.getCorporateRegistrationCode(),
                    )
else:
  organisation.edit(role = 'entreprise/siege',
                corporate_registration_code = request_eform.getCorporateRegistrationCode(),
                source_reference = request_eform.getCorporateRegistrationCode(),
                default_address_street_address=request_eform.getWorkAddress(),
                description = "Harmonisation d'une personne morale")

#Activate Organisation and update security
organisation.activerEntreprise()
organisation.updateLocalRolesOnSecurityGroups()
# Update the request_eform with the allocated number
request_eform.edit(registration_number = new_registry_number,
                   second_registration_number = new_registry_number,
                   second_date = request_eform.getDate(),
                   second_place = request_eform.getDefaultAddressCity(),
)
# Update the registration date of the request_eform with the time when the registry officer
#validates the transition
history_list = context.portal_workflow.getInfoFor(request_eform,'history', wf_id='egov_form_validation_workflow')
for history in history_list:
  if history['action'] == 'validate_action':
    request_eform.edit(registration_date=history['time'],
                       second_registration_date=history['time'])
# Get all M0 Bis attached to the request_eform and update them
for M0_bis in M0_bis_list:
  M0_bis.edit(title = request_eform.getTitle(),
              second_registration_number = new_registry_number,
              second_date = request_eform.getDate(),
              second_place = request_eform.getDefaultAddressCity(),
              second_registration_date = request_eform.getRegistrationDate(),
              source_reference = request_eform.getSourceReference(),
              corporate_registration_code=new_registry_number)
