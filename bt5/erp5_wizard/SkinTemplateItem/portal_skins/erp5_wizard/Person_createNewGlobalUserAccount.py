portal = context.getPortalObject()

if person is None:
  person = context

kw = context.Person_getDataDict(person=person)
kw['password'] = password

# explicitly check if username is unique
if portal.Base_validatePersonReference(kw['reference'], context.REQUEST):
  # create user in Authentification Server
  kw['start_assignment'] = len(person.Person_getAvailableAssignmentValueList())
  portal.portal_wizard.callRemoteProxyMethod(
                         'WitchTool_createNewGlobalUserAccountFromExpressInstance', \
                         use_cache = 0, \
                         ignore_exceptions = 0, \
                         **kw)
else:
  # user reference is NOT unique (valid) in Nexedi ERP5
  raise ValueError("User reference not unique")
