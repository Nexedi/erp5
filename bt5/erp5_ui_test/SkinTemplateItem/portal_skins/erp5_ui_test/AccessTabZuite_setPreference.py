"""Set a preference"""
preference_tool = context.portal_preferences
preference = getattr(preference_tool, "access_tab_test_preference", None)

if preference is None:
  preference = preference_tool.newContent(id="access_tab_test_preference",\
                                              portal_type="Preference")

if preference.getPreferenceState() != "enabled":
  preference.enable()

return 'Set Preference Successfully.'
