"""
  This script is used to create the new credential recovery
  Proxy : Manager proxy role is required to make possible for
anonymous to create a new Credential Recovery
"""

def createCredentialRecovery(**kw):
  module = portal.getDefaultModule(portal_type='Credential Recovery')
  credential_recovery = module.newContent(
                portal_type="Credential Recovery",
                **kw)
  credential_recovery.submit()

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
keep_items = {}
web_site = context.getWebSiteValue()
document_reference = None
if default_email_text is not None:
  # Case for recovery of username
  if person_list is None:
    query_kw = {'email.url_string':{'query':default_email_text, 'key':'ExactMatch'}}
    result = portal.portal_catalog(portal_type="Email", parent_portal_type="Person", **query_kw)
    if len(result) == 0:
      portal_status_message = portal.Base_translateString("Can't find corresponding person, it's not possible to update your credentials.")
      if web_site is not None:
        return web_site.Base_redirect('login_form', keep_items = dict(portal_status_message=portal_status_message ))
      return portal.Base_redirect('login_form', keep_items = dict(portal_status_message=portal_status_message ))

    person_list = [x.getObject().getParentValue() for x in result]

  # Create recovery
  message = "We have sent you an email containing your username(s). Please check your inbox and your junk/spam mail for this email."
  if web_site:
    document_reference = web_site.getCredentialUsernameRecoveryMessageReference()
  createCredentialRecovery(default_email_text=default_email_text,
                           destination_decision_value_list=person_list,
                           document_reference=document_reference,
                           language=portal.Localizer.get_selected_language())
else:
  # Case for recovery of password
  if person_list is None:
    user_list = context.acl_users.searchUsers(
      login=reference,
      login_portal_type='ERP5 Login',
      exact_match=True,
    )
    if len(user_list) != 1:
      portal_status_message = portal.Base_translateString("Can't find corresponding person, it's not possible to recover your credentials.")
      if web_site is not None:
        return web_site.Base_redirect('', keep_items = dict(portal_status_message=portal_status_message ))
      return portal.Base_redirect('', keep_items = dict(portal_status_message=portal_status_message ))
    person = portal.restrictedTraverse(user_list[0]['path'])
  else:
    person = person_list[0]
  # Check the response
  question_free_text = person.getDefaultCredentialQuestionQuestionFreeText()
  question_title = person.getDefaultCredentialQuestionQuestionTitle()
  question_answer = person.getDefaultCredentialQuestionAnswer()
  question_answer = question_answer and question_answer.lower()
  answer = default_credential_question_answer and default_credential_question_answer.lower() or ''
  message = "We have sent you an email to enable you to reset your password. Please check your inbox and your junk/spam mail for this email and follow the link to reset your password."
  if web_site:
    document_reference = web_site.getCredentialPasswordRecoveryMessageReference()

  if (question_title or question_free_text) and (answer == question_answer):
    createCredentialRecovery(reference=reference,
                  default_credential_question_answer=default_credential_question_answer,
                  destination_decision_value=person,
                  document_reference=document_reference,
                  language=portal.Localizer.get_selected_language())
  elif (question_free_text is None and question_answer is None) or \
    not portal_preferences.isPreferredAskCredentialQuestion():
    createCredentialRecovery(reference=reference,
                  destination_decision_value=person,
                  document_reference=document_reference,
                  language=portal.Localizer.get_selected_language())
  else:
    message = "You didn't enter the correct answer."
    keep_items = {'default_credential_question_question_free_text': question_free_text,
                  'default_credential_question_question_title': question_title,
                  'reference': reference}

keep_items['portal_status_message'] = portal.Base_translateString(message)
if web_site is not None:
  return web_site.Base_redirect(form_id='login_form', keep_items=keep_items)
return portal.Base_redirect(form_id='login_form', keep_items=keep_items)
