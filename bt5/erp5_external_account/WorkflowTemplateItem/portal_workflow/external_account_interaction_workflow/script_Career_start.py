"""
  Create respective accounts for a company employee.
"""
portal = context.getPortalObject()

career = state_change['object']
person = career.getParentValue()

default_email_text = person.Person_getDefaultExternalEmailText()
username, domain = default_email_text.split('@', 2)
if domain in portal.portal_preferences.getPreferredManagedExternalDomainNameList():
  # find (or create an external Email Account instance)
  kw = {'email.url_string':default_email_text,
        'default_source_uid': person.getUid(),
        'validation_state': 'validated',
        'portal_type': "Email Account"}
  email_account = portal.portal_catalog.getResultValue(**kw)
  if email_account is None:
    # might be invalidate temporary
    kw['validation_state'] = 'invalidated'
    email_account = portal.portal_catalog.getResultValue(**kw)
    if email_account is not None:
      email_account.validate()
    else:
      # no external account at all so create it
      email_account = portal.external_account_module.newContent(
                                                       portal_type = "Email Account",
                                                       url_string = default_email_text,
                                                       source_value = person)
      email_account.validate()
