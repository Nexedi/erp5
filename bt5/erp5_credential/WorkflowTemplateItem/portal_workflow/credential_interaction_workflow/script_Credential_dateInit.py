"""Specify the start date of the credential with the transition date"""
document = state_change['object']
if not document.hasStartDate():
  document.setStartDate(state_change.getDateTime())
if not document.hasStopDate():
  portal_preferences = document.getPortalObject().portal_preferences
  document.setStopDate(document.getStartDate() + portal_preferences.getPreferredCredentialRecoveryExpirationDay())
