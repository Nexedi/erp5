context.Zuite_setPreference('')
pref = context.portal_preferences.erp5_ui_test_preference

pref.setPreferredTextEditor('fck_editor')
pref.setPreferredTextFormat('text/html')

return 'Set CRM Preference Successfully.'
