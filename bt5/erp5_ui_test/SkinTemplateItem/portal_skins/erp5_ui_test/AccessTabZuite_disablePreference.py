"""Disable erp5_ui_test_preference preference"""
preference_tool = context.portal_preferences
preference = getattr(preference_tool, "access_tab_test_preference", None)
if preference is not None:
  preference.disable()
  # enable the erp5_ui_test_preference again....
  erp5_ui_test_preference = getattr(context.portal_preferences, "erp5_ui_test_preference", None)
  if erp5_ui_test_preference is not None and \
       erp5_ui_test_preference.getPreferenceState() in ('draft', 'disabled'):
    erp5_ui_test_preference.enable()

return 'Disabled Preference Successfully.'
