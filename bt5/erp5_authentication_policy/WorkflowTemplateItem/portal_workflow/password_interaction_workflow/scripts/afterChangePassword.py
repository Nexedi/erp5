login = state_change['object']
portal = login.getPortalObject()

# check preferences and save only if set

if portal.portal_preferences.getPreferredNumberOfLastPasswordToCheck() or \
    portal.portal_preferences.getPreferredMaxPasswordLifetimeDuration() is not None:
  # save password and modification date
  current_password = login.getPassword()
  if current_password is not None:
    portal.system_event_module.newContent(
      # Person_isPasswordExpired cache the wrong result if document is not in catalog.
      immediate_reindex=True,
      portal_type='Password Event',
      source_value=login,
      destination_value=login,
      password=current_password,
    ).confirm()
