"""
This script collects *all* filled properties in the P2
request_eform and updates the person and the organisation already
created with the P0.
"""

# Initalize some useful variables
from Products.ZSQLCatalog.SQLCatalog import ComplexQuery
from Products.ZSQLCatalog.SQLCatalog import Query
from Products.DCWorkflow.DCWorkflow import ValidationFailed
request_eform = state_change['object']
portal = request_eform.getPortalObject()
organisation_module = portal.organisation_module
person_module = portal.person_module

date = request_eform.getDate()
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
  type_of_form = 'M'
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
group = (date.year(),)
new_registry_number = request_eform.portal_ids.generateNewId(
                                     id_group = group,
                                     method = attachLocationYearInfo)

#variable used to store activity of the organisation,activities should be separated with commas, and no space between them
activity_list=[]
request_eform.setTitle(request_eform.getOwnerFirstName()+' '+request_eform.getOwnerLastName())
#build a query to search for the merchant
query=ComplexQuery(Query(title=request_eform.getTitle()),
             Query(birth_date=request_eform.getOwnerBirthday()),
             Query(birthplace_city=request_eform.getOwnerBirthplace()),
             logical_operator="AND")
person_list=[person.getObject() for person in \
       context.portal_catalog(portal_type='Person',query=query)]

if len(person_list) >1 :
  raise ValidationFailed("Error : There is more than one person with the "\
            " title '%s', birth date '%s' and birthplace '%s'" % (
                request_eform.getTitle(),
                request_eform.getOwnerBirthday(),
                request_eform.getOwnerBirthplace()))
elif len(person_list) == 0:
  raise ValidationFailed("Error : There is nobody with the "\
            " title '%s', birth date '%s' and birthplace '%s'" % (
                request_eform.getTitle(),
                request_eform.getOwnerBirthday(),
                request_eform.getOwnerBirthplace()))

else:
  # Modify person based on properties filled in P2
  person = person_list[0]
  person.edit(first_name=request_eform.getOwnerFirstName(),
              last_name=request_eform.getOwnerLastName(),
              start_date=request_eform.getOwnerBirthday(),
              default_birthplace_address_city=request_eform.getOwnerBirthplace(),
              default_address_street_address=request_eform.getOwnerAddress(),
              nationality=request_eform.getOwnerCitizenship())
  if request_eform.getOwnerMarriedCheck():
    person.edit(marital_status='married')
  elif request_eform.getOwnerDivorcedCheck():
    person.edit(marital_status='divorced')
  elif request_eform.getOwnerSingleCheck():
    person.edit(marital_status='single')
  elif request_eform.getOwnerWidowerCheck():
    person.edit(marital_status='widowed')
  # Modify also the person's organisation whether its activities are changed, or its
  #address, or its corporate name or whether the P2 form is used to create another
  #company for the person
  if request_eform.getCompanyModifications():
    corporate_registration_code = request_eform.getCompanyCorporateRegistrationCode()
    request_eform.edit(corporate_registration_code=corporate_registration_code)
    organisation_list = [organisation.getObject() for organisation in \
        organisation_module.searchFolder(corporate_registration_code=request_eform.getCorporateRegistrationCode())]
    for organisation in organisation_list:
      activity_free_text = organisation.getActivityFreeText()
      activity_list = activity_free_text and activity_free_text.split(',') or []
      if request_eform.getTransferCheck():
        organisation.edit(default_address_street_address = request_eform.getCompanyAddress())
        organisation.getDefaultAddress().transfer()

      elif request_eform.getActivityCheck():
        if request_eform.getCompanyModifiedRemovedActivities() != None:
          removed_activities_list = request_eform.getCompanyModifiedRemovedActivities().split(',')
          for removed_activities in removed_activities_list:
            if removed_activities in activity_list:
              activity_list.remove(removed_activities)
              organisation.edit(activity_free_text = ','.join(activity_list))
        if request_eform.getCompanyModifiedAddedActivities() != None:
          activity_list.append(request_eform.getCompanyModifiedAddedActivities())
          organisation.edit(activity_free_text = ','.join(activity_list))

      elif request_eform.getCompanyModifiedName() != None:
        if request_eform.getCompanyOldName() == None:
          organisation_module = context.getPortalObject().organisation_module
          second_organisation = organisation_module.newContent(portal_type='Organisation')
          second_organisation.edit(title=request_eform.getCompanyModifiedName(),
                                   corporate_name = request_eform.getCompanyModifiedName(),
                                   corporate_registration_code = new_registry_number,
                                   activity_free_text = request_eform.getCompanyModifiedAddedActivities(),
                                   role='commerce/siege',)
          assignment = person.newContent(portal_type='Assignment')
          assignment.edit(function = 'commerce/commercant',
                     destination_form_value = request_eform,
                     destination_value = second_organisation)
          assignment.openSubmit()
          assignment.open()
        else:
          organisation.edit(title = request_eform.getCompanyModifiedName(),
                            corporate_name = request_eform.getCompanyModifiedName())
  #If the person has secondaries organisations,
  #modify the secondaries organisations for the person
  elif request_eform.getEstablishmentModification():
    corporate_registration_code = request_eform.getEstablishmentRegistrationCode()
    request_eform.edit(corporate_registration_code=corporate_registration_code)
    organisation_list = [organisation.getObject() for organisation in \
        organisation_module.searchFolder(corporate_registration_code=request_eform.getCorporateRegistrationCode())]
    for organisation in organisation_list:
      if request_eform.getClosingCheck():
        organisation.getDefaultAddress().close()
      elif request_eform.getTransferCheck():
        organisation.edit(default_address_street_address = request_eform.getCompanyAddress())
        organisation.getDefaultAddress().transfer()
      elif request_eform.getBuyersName() != None:
        organisation.getDefaultAddress().sell()
      else:
        organisation.edit(activity_free_text = request_eform.getModifiedAddedActivities())
        organisation.getDefaultAddress().modify()


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
