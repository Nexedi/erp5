portal = context.getPortalObject()

if person is None:
  person = context

kw = context.Person_getDataDict(person=person)

# explicitly check if username is unique
if portal.WizardTool_isPersonReferencePresent(kw['reference']):
  # create assignment for user in Authentification Server
  portal.portal_wizard.callRemoteProxyMethod(
                         'WitchTool_createNewAssignmentForExistingPerson',
                         use_cache = 0,
                         ignore_exceptions = 0,
                         **kw)
else:
  raise ValueError("User does not exist yet")
