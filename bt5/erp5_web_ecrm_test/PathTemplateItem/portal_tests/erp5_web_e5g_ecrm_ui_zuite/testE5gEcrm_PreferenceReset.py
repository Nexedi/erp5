"""Reset everything for the test"""

pref = getattr(context.portal_preferences, "erp5_ui_test_preference", None)
if pref is None:
  pref = context.portal_preferences.newContent(id="erp5_ui_test_preference", portal_type="Preference")
pref.setPreferredListboxViewModeLineCount(None)
pref.setPreferredListboxListModeLineCount(10)
if pref.getPreferenceState() == 'disabled':
  pref.enable()
else:
  context.portal_caches.clearAllCache()

return 'Reset Successfully.'
