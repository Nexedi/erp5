from Products.ERP5Type.ImmediateReindexContextManager import ImmediateReindexContextManager
changed_object = state_change['object']

portal = changed_object.getPortalObject()
organisation_module = portal.getDefaultModule(portal_type='Organisation')


result = changed_object.portal_catalog(portal_type='Organisation',
           vat_code=changed_object.getCompanyNineaNumber())

# if the organisation don't exists, create it
if not len(result):
  organisation = organisation_module.newContent(\
      portal_type='Organisation',
      title=changed_object.getCompanyName(),
      corporate_name=changed_object.getCompanyName(),
      address_street_address=changed_object.getCompanyAddress(),
      address_city=changed_object.getCityName(),
      corporate_registration_code=changed_object.getCompanyRccmNumber(),
      vat_code=changed_object.getCompanyNineaNumber(),
      activity_code=changed_object.getCompanyCofiNumber(),
      default_email_text=changed_object.getCompanyEmail(),
      acronym=changed_object.getCompanySigle(),
      default_telephone_text=changed_object.getCompanyPhoneNumber(),
      default_fax_text=changed_object.getCompanyFaxNumber(),
      )
else:
  organisation = result[0].getObject()

# create the person wich represent the company
person_module = portal.getDefaultModule(portal_type='Person')
with ImmediateReindexContextManager() as immediate_reindex_context_manager:
  accountant = person_module.newContent(portal_type='Person',
                           immediate_reindex=immediate_reindex_context_manager,
                           title=changed_object.getAccountantName(),
                           default_telephone_text=changed_object.getAccountantTelNumber(),
                           default_fax_text=changed_object.getAccountantFax(),
                           default_email_text=changed_object.getAccountantEmail(),
                           address_street_address=changed_object.getAccountantAddress(),
                           address_city=changed_object.getAccountantCity(),
                           career_subordination_value=organisation)


  # create an assignment to be able to login :
  assignment = accountant.newContent(portal_type='Assignment')
  assignment.setStartDate(DateTime())
  assignment.setStopDate(DateTime()+365)
  assignment.setCareerFunction(changed_object.getAccountantFunction())
  assignment.open()

  # set the login and password required a manager role, so a script with a
  # proxy role is used
  login = context.generateNewLogin(text=changed_object.getAccountantName())
  password = changed_object.Person_generatePassword()
  context.EGov_setLoginAndPasswordAsManager(accountant, login, password)

accountant.Person_sendCrendentialsByEMail()
