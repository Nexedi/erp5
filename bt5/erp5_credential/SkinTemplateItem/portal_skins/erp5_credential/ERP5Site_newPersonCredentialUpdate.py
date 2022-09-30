"""Create a credential update in relation with the person object of current user"""
portal = context.getPortalObject()
user = portal.portal_membership.getAuthenticatedMember()
person = user.getUserValue()
login = user.getLoginValue()

if person is None:
  portal_status_message = "Can't find corresponding person, it's not possible to update your credentials."
elif login is None:
  portal_status_message = "Can't find corresponding login, it's not possible to update your credentials."
else:
  # create the credential update
  module = portal.getDefaultModule(portal_type='Credential Update')
  credential_update = module.newContent(
    portal_type="Credential Update",
    reference=login.getReference(),
    first_name=first_name,
    last_name=last_name,
    gender=gender,
    nationality=nationality,
    default_credential_question_question=default_credential_question_question,
    default_credential_question_question_free_text=default_credential_question_question_free_text,
    default_credential_question_answer=default_credential_question_answer,
    default_email_text=default_email_text,
    default_telephone_telephone_country=default_telephone_telephone_country,
    default_telephone_text=default_telephone_text,
    default_mobile_telephone_telephone_country=default_mobile_telephone_telephone_country,
    default_mobile_telephone_text=default_mobile_telephone_text,
    default_fax_text=default_fax_text,
    default_address_street_address=default_address_street_address,
    default_address_city=default_address_city,
    default_address_zip_code=default_address_zip_code,
    default_address_region=default_address_region,
    function=function,
    activity_list=activity_list,
    skill_list=skill_list,
    date_of_birth=date_of_birth,
    destination_decision=person.getRelativeUrl(),
    default_image_file=default_image_file,
    description=description)

  if password:
    credential_update.edit(password=password)

  credential_update.submit()
  portal_status_message = "Credential Update Created."

  # if we are changing password for current logged in user then do it
  # within same transaction and update client side credentials cookie
  if password:
    # The password is updated synchronously and the the rest of the credential Update is done later
    login_reference = credential_update.Credential_updatePersonPassword()
    portal.cookie_authentication.credentialsChanged(
      person.Person_getUserId(),
      login_reference,
      password,
    )
    portal_status_message = "Password changed."

portal_status_message = context.Base_translateString(portal_status_message)
return portal.Base_redirect(keep_items = {'portal_status_message': portal_status_message})
