"""
This script collects *all* filled properties in the M2
request_eform and updates the organisation already created with the M0.
"""
# Initalize some useful variables
request_eform = state_change['object']
portal = request_eform.getPortalObject()
organisation_module = portal.organisation_module
person_module = portal.person_module
corporate_registration_code = request_eform.getCorporateRegistrationCode()
new_corporate_name = request_eform.getTitle()
new_headquarters = request_eform.getNewHeadquarters()
old_headquarters = request_eform.getOldHeadquarters()
old_legal_form = request_eform.getOldLegalForm()
old_capital = request_eform.getOldCapital()
added_activities = request_eform.getAddedActivities()
removed_activities = request_eform.getDeletedActivities()
application_date = request_eform.getDate()
company_check = request_eform.getCompanyCheck()
transfer_check = request_eform.getTransferCheck()
transferred_address = request_eform.getTransferredAddress()
closing_check = request_eform.getClosingCheck()
default_address_city = request_eform.getDefaultAddressCity()
new_address = request_eform.getNewAddress()

caracteristic_property_dict={\
    'social_form':request_eform.getNewLegalForm(),
    'social_capital':request_eform.getNewCapital(),
    'title':request_eform.getNewTitle(),
  }

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
  type_of_form = 'M'
  last_corporate_registration_code = str(str(last_id).split('-').pop())
  new_corporate_registration_code  = '%05d' % int(str(int(last_corporate_registration_code)+1))
  return ('-'.join(['SN', location_initials, year,
    type_of_form,new_corporate_registration_code]))

# We shall now allocate a new registry number
# using custom method attachLocationYearInfo
# we use corporate_registry for corporations and
# merchant_registry for merchants.
group = (application_date.year(),)

new_registry_number = request_eform.portal_ids.generateNewId(
                                     id_group = group,
                                     method = attachLocationYearInfo)


#variable used to store activity of the organisation,activities should be
#separated with commas, and no space between them
# Modify the organisation whether its activities are changed, or its address,
#or its characteristics
activity_list=[]
organisation_list = [organisation.getObject() for organisation in \
                     organisation_module.searchFolder(corporate_registration_code=corporate_registration_code)]
for organisation in organisation_list:
  if organisation.getActivityFreeText()!= None:
    activity_list = organisation.getActivityFreeText().split(',')

  # Open all assignemnts that are in open_submitted state
  destination_form_uid = context.portal_categories.destination_form.getUid()
  assignment_list = [assignment.getObject() for assignment in context.portal_catalog(portal_type='Assignment',
                        validation_state = 'open_submitted',
                        destination_form_uid = request_eform.getUid())]
  for assignment in assignment_list:
    assignment.open()
    assignment.edit(destination_value=organisation)

  if request_eform.getMoralPersonCheck():
    if request_eform.getCharacteristicsCheck():
      for property, value in caracteristic_property_dict.items():
        if value is not None: # check someting has been entered in the property field
          organisation.setProperty(property, value)
    if request_eform.getActivitiesCheck():
      if removed_activities != None:
        removed_activity_list = removed_activities.split(',')
        for removed_activity in removed_activity_list:
          if removed_activity in activity_list:
            activity_list.remove(removed_activity)
      if added_activities != None:
        added_activity_list = added_activities.split(',')
        for added_activity in added_activity_list:
          if added_activity not in activity_list:
            activity_list.append(added_activity)
      organisation.edit(activity_free_text = ','.join(activity_list),
                        org_modification_date = request_eform.getAddedActivitiesDate() or request_eform.getDeletedActivitiesDate())
    if request_eform.getTransferCheck():
      if request_eform.getClosingCheck():
        organisation.edit(default_address_street_address = new_headquarters)
        organisation.getDefaultAddress().close()
      else:
        organisation.edit(default_address_street_address = new_headquarters,
             default_address_city = default_address_city)
        organisation.getDefaultAddress().transfer()

##Changes in secondaries organisations
new_corporate_registration_code = request_eform.getNewCorporateRegistrationCode()
if new_corporate_registration_code != None:
  second_organisation_list = [organisation.getObject() for organisation in \
                              organisation_module.searchFolder(corporate_registration_code=new_corporate_registration_code)]
  for second_organisation in second_organisation_list:
    if request_eform.getCompanyCheck() and request_eform.getTransferCheck():
      if request_eform.getClosingCheck():
        second_organisation.edit(org_modification_date = request_eform.getClosedDate())
        second_organisation.getDefaultAddress().close()
      else: 
        second_organisation.edit( default_address_street_address = new_address,
                                  default_address_city = default_address_city,
                                  org_modification_date = request_eform.getTransferredDate())
        second_organisation.getDefaultAddress().transfer()
    elif request_eform.getCompanyCheck() and request_eform.getBuyersName() != None:
      second_organisation.edit(org_modification_date = request_eform.getBuyersDate())
      second_organisation.getDefaultAddress().sell()
    else:
      second_organisation.getDefaultAddress().modify()


# Update the request_eform with the allocated number
request_eform.edit(registration_number = new_registry_number,
                   second_date = application_date,
                   second_registration_number = new_registry_number,
                   second_place = default_address_city)
# Update the registration date of the request_eform with the time when the registry officer
#validates the transition
history_list = request_eform.portal_workflow.getInfoFor(request_eform,
                                                'history',
                                                wf_id = 'egov_form_validation_workflow')
for history in history_list:
  if history['action'] == 'validate_action':
    request_eform.edit(registration_date = history['time'],
                       second_registration_date = history['time'])
# Get all M2 Bis attached to the request_eform and update them
m2_bis_result = request_eform.contentValues(portal_type='M2 Bis')
m2_bis_list = [form.getObject() for form in m2_bis_result]

for m2_bis in m2_bis_list:
  if request_eform.getActivityCheck():
    activity_list = organisation.getActivityFreeText().split(',')
    added_activities = m2_bis.getActivityFreeText()
    if added_activities:
      added_activity_list = added_activities.split(',')
      for added_activity in added_activity_list:
        if added_activity not in activity_list:
          activity_list.append(added_activity)
      organisation.edit(activity_free_text = ','.join(activity_list))
