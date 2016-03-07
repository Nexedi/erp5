portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
searchAndActivate_ = portal.portal_catalog.searchAndActivate
def searchAndActivate(**kw):
  searchAndActivate_('Credential_accept', **kw)

portal_type_list = []
if portal_preferences.getPreferredCredentialRequestAutomaticApproval():
  portal_type_list.append('Credential Request')
if portal_preferences.getPreferredCredentialRecoveryAutomaticApproval():
  portal_type_list.append('Credential Recovery')
if portal_type_list:
  searchAndActivate(
    portal_type=portal_type_list,
    validation_state='submitted',
  )

credential_update_destination_decision_portal_type_list = []
if portal_preferences.getPreferredPersonCredentialUpdateAutomaticApproval():
  credential_update_destination_decision_portal_type_list.append('Person')
if portal_preferences.getPreferredOrganisationCredentialUpdateAutomaticApproval():
  credential_update_destination_decision_portal_type_list.append('Organisation')
if credential_update_destination_decision_portal_type_list:
  searchAndActivate(
    portal_type='Credential Update',
    destination_decision_portal_type=credential_update_destination_decision_portal_type_list,
    validation_state='submitted',
  )
