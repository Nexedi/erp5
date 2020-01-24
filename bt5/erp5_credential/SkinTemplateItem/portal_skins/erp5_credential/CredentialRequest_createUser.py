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

login_list = [x for x in person.objectValues(portal_type='ERP5 Login') \
              if x.getValidationState() == 'validated']
if len(login_list):
  login = login_list[0]
else:
  login = person.newContent(portal_type='ERP5 Login')
# Create user of the person only if not exist
user_id = person.Person_getUserId()
if user_id and login.hasPassword():
  return user_id, None

# Set login
reference = context.getReference()
if not login.hasReference():
  if not reference:
    raise ValueError, "Impossible to create an account without login"
  login.setReference(reference)
  if not user_id:
    person.setUserId(reference)

password = None
# Set password if no password on the Login
if not login.hasPassword():
  if context.getPassword():
    #User has fill a password
    password = context.getPassword()
    login.setEncodedPassword(password)
  else:
    if not portal_preferences.isPreferredSystemGeneratePassword():
      # user will set it trough a credential recovery process
      password = None
      module = portal.getDefaultModule(portal_type='Credential Recovery')
      credential_recovery = module.newContent(
                                     portal_type="Credential Recovery",
                                     reference=reference,
                                     destination_decision=person.getRelativeUrl(),
                                     language=portal.Localizer.get_selected_language())
      credential_recovery.submit()
    else:
      # system should generate a password
      password = context.Person_generatePassword()
      login.setPassword(password)

  # create a global account
  if context.ERP5Site_isSingleSignOnEnable():
    #The master manage encoded password and clear password
    person.Person_createNewGlobalUserAccount(password=password)
    person.Person_validateGlobalUserAccount()

  if login.getValidationState() == 'draft':
    login.validate()
else:
  #Person has an already an account
  if context.ERP5Site_isSingleSignOnEnable():
    #Check assignment for the current instance
    person.Person_validateGlobalUserAccount()

return reference, password
