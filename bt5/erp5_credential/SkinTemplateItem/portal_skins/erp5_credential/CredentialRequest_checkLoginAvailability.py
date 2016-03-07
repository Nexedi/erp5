"""Check login is available locally and globally for instance with SSO.
Parameters:
value -- field value (string)
REQUEST -- standard REQUEST variable"""

if value:
  # Same tag is used as in Document.Person._setReference, in order to protect against
  # concurrency between Credential Request and Person object too
  tag = 'Person_setReference_%s' % value.encode('hex')
  if context.getPortalObject().portal_activities.countMessageWithTag(tag):
    return False

def getRealContext():
  if not REQUEST:
    return context
  object_path = REQUEST.get("object_path")
  portal = context.getPortalObject()
  return portal.restrictedTraverse(object_path)

#Allow user to create a request with it's username
member = context.portal_membership.getAuthenticatedMember()
if member is not None \
   and member.getUserName() == value \
   and value != "Anonymous User":
  return True

context = getRealContext()
#Allow reference for person in relation with the credential request
if context.getPortalType() == "Credential Request":
  related_person = context.getDestinationDecisionValue(portal_type="Person")
  if related_person is not None:
    if related_person.getReference() == value:
      return True

#check no pending credential request with this user name
#Don't take in case the current credential 
module = context.getDefaultModule("Credential Request")
credential_request_count_result = module.countFolder(reference=value,
                                                     uid="NOT %s" % context.getUid(),
                                                     validation_state=["draft", "submitted"])

if credential_request_count_result[0][0] > 0:
  return False

#check local account
if not context.ERP5Site_isLocalLoginAvailable(value):
  return False

if context.ERP5Site_isSingleSignOnEnable():
  #check username is unique and valid
  if not context.WizardTool_isPersonReferenceGloballyUnique(editor=value,
                                                   request=REQUEST, 
                                                   ignore_users_from_same_instance=0):
    return False

return True
