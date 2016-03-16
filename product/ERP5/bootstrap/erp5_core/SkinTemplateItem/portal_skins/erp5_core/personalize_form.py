# make default CMF personalize_form redirect to the preference tool

preference_tool = context.getPortalObject().portal_preferences

preference = preference_tool.getActivePreference()

if preference is not None and preference.getPriority() == 3: # XXX: 3 is Priority.USER
  return preference.Base_redirect('view')

return preference_tool.Base_redirect('view')
