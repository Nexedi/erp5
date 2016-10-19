'''
  Try to find the question related to the user passed in parameter.
  Proxy : this required a manager proxy role to be able to search in all persons
'''
portal = context.getPortalObject()
request  = context.REQUEST
web_site = context.getWebSiteValue()
if web_site:
  request.set("came_from", web_site.absolute_url())
if choice == "password":
  request.set('reference', reference)
  user_id = portal.Base_getUserIdByUserName(reference)
  if user_id is None:
    person = None
  else:
    person = portal.Base_getUserValueByUserId(user_id)
  if person is None:
    portal_status_message = context.Base_translateString("Could not find your user account.")
    if web_site:
      return web_site.Base_redirect('login_form', keep_items = dict(portal_status_message=portal_status_message ))
    return portal.Base_redirect('login_form', keep_items = dict(portal_status_message=portal_status_message ))

  #If any question, we can create directly the credential recovery
  question_free_text = person.getDefaultCredentialQuestionQuestionFreeText()
  question_title = person.getDefaultCredentialQuestionQuestionTitle()

  if not (question_free_text or question_title) or \
    not portal.portal_preferences.isPreferredAskCredentialQuestion():
    return context.ERP5Site_newCredentialRecovery(reference=reference)

  web_section = context.getWebSectionValue()
  if web_section is not None:
    return web_section.Base_redirect('question',
                               keep_items = \
                                  dict(default_credential_question_question_free_text=question_free_text,
                                      default_credential_question_question_title=question_title,
                                      reference=reference))
  else:
    return context.Base_redirect('ERP5Site_newCredentialRecoveryDialog',
                               keep_items = \
                                  dict(default_credential_question_question_free_text=question_free_text,
                                      default_credential_question_question_title=question_title,
                                      reference=reference))
elif choice == "username":
  query_kw = {"email.url_string" : default_email_text}
  result = portal.portal_catalog(portal_type="Email", parent_portal_type="Person", **query_kw)
  person_list = [x.getParentValue() for x in result]
  person_list = [x for x in person_list if x.getReference()] # only consider persons with a valid login
  if len(person_list) == 0:
    portal_status_message = context.Base_translateString("Could not find your user account.")
    if web_site:
      return web_site.Base_redirect('login_form', keep_items = dict(portal_status_message=portal_status_message ))
    return portal.Base_redirect('login_form', keep_items = dict(portal_status_message=portal_status_message ))
  return context.ERP5Site_newCredentialRecovery(default_email_text=default_email_text, person_list=person_list)
