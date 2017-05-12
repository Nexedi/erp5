# make default CMF personalize_form redirect to the preference tool

preference_tool = context.getPortalObject().portal_preferences

preference = preference_tool.getActiveUserPreference()

if preference is not None:
  return preference.Base_redirect('view')

return preference_tool.Base_redirect('view')
