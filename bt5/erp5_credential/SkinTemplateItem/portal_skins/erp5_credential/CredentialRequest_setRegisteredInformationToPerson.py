"""Copy subscription information to related person
Proxy:
Assignee -- allow to modify the related person"""

# check the script is not called from a url
if REQUEST is not None:
  return None

from Products.ERP5Type.Errors import UnsupportedWorkflowMethod

context.Credential_checkConsistency(['Person'])
person = context.getDestinationDecisionValue(portal_type="Person")

#Close the current career and create new career if needed
default_career = getattr(person,'default_career',None)
if default_career is not None:
  try:
    default_career.stop("New credential")
    default_career.setStopDate(DateTime())
    person.Person_shiftDefaultCareer()

  except UnsupportedWorkflowMethod:
    pass

# Person Mapping
person_mapping = (
    # (subscription, person)
    ('first_name', 'first_name'),
    ('last_name', 'last_name'),
    ('gender', 'gender'),
    ('default_telephone_text', 'default_telephone_text'),
    ('default_mobile_telephone_text', 'default_mobile_telephone_text'),
    ('default_email_text', 'default_email_text'),
    ('date_of_birth', 'start_date'),
    ('nationality', 'nationality'),
    ('skill_list', 'default_career_skill_list'),
    ('activity_list', 'default_career_activity_list'),
    ('default_fax_text', 'default_fax_text'),
    ('default_address_street_address', 'default_address_street_address'),
    ('default_address_zip_code', 'default_address_zip_code'),
    ('default_address_city', 'default_address_city'),
    ('default_address_region', 'default_address_region'),
    ('function_list', 'default_career_function_list'),
    ('role_list', 'default_career_role_list'),
    ('default_credential_question_answer', 'default_credential_question_answer'),
    ('default_credential_question_question', 'default_credential_question_question'),
    ('default_credential_question_question_free_text', 'default_credential_question_question_free_text'),
    )

context.Credential_copyRegistredInformation(person, person_mapping)

#try to validate, can be get error if already validated
try:
  person.validate()
except UnsupportedWorkflowMethod:
  pass

#Get the default career
default_career = getattr(person,'default_career',None)

#Set the person subordination if we have a relative organisation on the credential
organisation = context.getDestinationDecisionValue(portal_type="Organisation")
if organisation is not  None:
  default_career.setSubordinationValue(organisation)

#Try to validate the default career
try:
  default_career.start()
  default_career.setStartDate(DateTime())
except UnsupportedWorkflowMethod:
  pass
