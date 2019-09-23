context.Zuite_setPreference('')
preference = context.portal_preferences.erp5_ui_test_preference
preference.edit(
  preferred_report_style='ODS',
  preferred_report_format='html'
)

return 'Set Deferred Preference Successfully.'
