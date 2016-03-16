"""
  Set reference and password to create a user. Create a global user if SSO enable.
  Proxy:
  Manager -- allow to set password on all account
"""

#Don't allow to call from url
if REQUEST:
  raise ValueError, "You can not call this script from the url"

portal = context.getPortalObject()
portal_preferences = context.portal_preferences
person = context.getDestinationDecisionValue(portal_type="Person")

# Create user of the person only if not exist
if person.hasReference() and person.getPassword():
  return person.getReference(), None

# Set login
login = context.getReference()
if not person.hasReference():
  if not login:
    raise ValueError, "Impossible to create an account without login"
  person.setReference(login)
else:
  login = person.getReference()

password = None
# Set password if no password on the person
if not person.getPassword():
  if context.getPassword():
    #User has fill a password
    password = context.getPassword()
    person.setEncodedPassword(password)
  else:
    if not portal_preferences.isPreferredSystemGeneratePassword():
      # user will set it trough a credential recovery process
      password = None
      module = portal.getDefaultModule(portal_type='Credential Recovery')
      credential_recovery = module.newContent(
                                     portal_type="Credential Recovery",
                                     reference=login,
                                     destination_decision=person.getRelativeUrl(),
                                     language=portal.Localizer.get_selected_language())
      credential_recovery.submit()
    else:
      # system should generate a password
      password = context.Person_generatePassword(alpha=5, numeric=3)
      person.setPassword(password)

  # create a global account
  if context.ERP5Site_isSingleSignOnEnable():
    #The master manage encoded password and clear password
    person.Person_createNewGlobalUserAccount(password=password)
    person.Person_validateGlobalUserAccount()
else:
  #Person has an already an account
  if context.ERP5Site_isSingleSignOnEnable():
    #Check assignment for the current instance
    person.Person_validateGlobalUserAccount()

return login, password
