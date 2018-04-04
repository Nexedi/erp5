"""Call by dialog to create a new credential request and redirect to the context
Paramameter list :
reference -- User login is mandatory (String)
default_email_text -- Email is mandatory (String)"""
# create the credential request
portal = context.getPortalObject()
module = portal.getDefaultModule(portal_type='Credential Request')
portal_preferences = portal.portal_preferences
category_list = portal_preferences.getPreferredSubscriptionAssignmentCategoryList()

if not context.CredentialRequest_checkLoginAvailability(reference):
  message_str = "Selected login is already in use, please choose different one."
  return portal.Base_redirect(keep_items = dict(portal_status_message=context.Base_translateString(message_str)))
 
credential_request = module.newContent(
                portal_type="Credential Request",
                first_name=first_name,
                last_name=last_name,
                reference=reference,
                password=password,
                default_credential_question_question=default_credential_question_question,
                default_credential_question_question_free_text=default_credential_question_question_free_text,
                default_credential_question_answer=default_credential_question_answer,
                default_email_text=default_email_text,
                default_telephone_text=default_telephone_text,
                default_mobile_telephone_text=default_mobile_telephone_text,
                default_fax_text=default_fax_text,
                default_address_street_address=default_address_street_address,
                default_address_city=default_address_city,
                default_address_zip_code=default_address_zip_code,
                default_address_region=default_address_region,
                role_list=role_list,
                function=function,
                site=site,
                activity_list=activity_list,
                corporate_name=corporate_name,
                date_of_birth=date_of_birth)

credential_request.setCategoryList(category_list)
# Same tag is used as in ERP5 Login._setReference, in order to protect against
# concurrency between Credential Request and Person object too
credential_request.reindexObject(activate_kw=dict(tag='set_login_%s' % reference.encode('hex')))

#We attach the current user to the credential request if not anonymous
if not context.portal_membership.isAnonymousUser():
  person = context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue()
  destination_decision = []
  if reference in [x.getReference() for x in person.objectValues(portal_type='ERP5 Login')
                   if x.getValidationState() == 'validated']:
    destination_decision.append(person.getRelativeUrl())
  if person.getDefaultCareerSubordinationTitle() == corporate_name:
    destination_decision.append(person.getDefaultCareerSubordination())
  if destination_decision:
    credential_request.setDestinationDecision(destination_decision)

if portal_preferences.getPreferredCredentialAlarmAutomaticCall():
  credential_request.submit("Automatic submit")
  message_str = "Credential Request Created."
else:
  if portal_preferences.isPreferredEmailVerificationCheck():
    # after_path_and_method_id argument is used below to not activate when
    # Crededial request object is not indexed yet. This is needed because when
    # the method searchAndActivate from catalog is called, if the object is not
    # indexed, the e-mail is not sent.
    method_id_list = ('immediateReindexObject', 'recursiveImmediateReindexObject')
    path_and_method_id = (credential_request.getPath(), method_id_list)
    activity_kw = dict(activity='SQLQueue',
                       after_path_and_method_id=path_and_method_id)
    credential_request.activate(**activity_kw).CredentialRequest_sendSubmittedNotification(
      context_url=context.absolute_url(),
      notification_reference='credential_request-subscription')
    message_str = "Thanks for your registration. You will be receive an email to activate your account."
  else:
    # no email verification is needed
    credential_request.submit("Automatic submit")
    message_str = "Credential Request Created."
    

return portal.Base_redirect(form_id='login_form', 
                     keep_items = dict(portal_status_message=context.Base_translateString(message_str)))
