portal = context.getPortalObject()
active_preference = portal.portal_preferences.getActiveUserPreference()
if not active_preference:
  active_preference = portal.portal_preferences.getActivePreference()

return active_preference.Base_redirect(form_id='Preference_viewAccounting')
