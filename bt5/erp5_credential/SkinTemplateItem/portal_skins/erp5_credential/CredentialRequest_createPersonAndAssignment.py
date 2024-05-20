"""
  For a credential request as context, we set the related person informations,
  the assignments of the person and send notificaiton email
  Proxy:
  Auditor -- allow to get credential request informations
"""

# check the script is not called from a url
if REQUEST is not None:
  return None


# XXX by default we don't want to automatically create/update organisation
# Someone should confirm this informations before creating the organisation
#if context.getOrganisationTitle():
#  related_portal_type.append('Organisation')

#Create related object, pass a copy of the dict
context.CredentialRequest_setDefaultDestinationDecision([x for x in related_portal_type])

# Check consistency of the subscription, pass a copy of the dict
context.Credential_checkConsistency([x for x in related_portal_type])

# Create assignment
context.CredentialRequest_updatePersonAssignment()

# Create account
login, password = context.CredentialRequest_createUser()

# Fill related object with credential request
for portal_type in related_portal_type:
  getattr(context,'CredentialRequest_setRegisteredInformationTo%s' % portal_type.replace(' ',''))()

# Update Local Roles
context.CredentialRequest_updateLocalRolesOnSecurityGroups()

if password is not None:
  if password.startswith('{SSHA}'):
    #password is encoded, set it to None to script witch send the password to user
    password = None
# Send notification in activities
context.activate(activity='SQLQueue').CredentialRequest_sendAcceptedNotification(login, password)
