"""
  Stop respective account for a company employee.
"""
portal = context.getPortalObject()

career = state_change['object']
person = career.getParentValue()

default_email_text = person.Person_getDefaultExternalEmailText()
username, domain = default_email_text.split('@', 2)
if domain in portal.portal_preferences.getPreferredManagedExternalDomainNameList():
  # find external Email Account instance and invalidate it
  kw = {'email.url_string': default_email_text,
        'default_source_uid': person.getUid(),
        'portal_type': 'Email Account',
        'validation_state': 'validated'}
  email_account = portal.portal_catalog.getResultValue(**kw)
  if email_account is not None:
    email_account.invalidate()
