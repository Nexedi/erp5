preference = context.portal_preferences.erp5_ui_test_preference
preference.setPreferredListboxViewModeLineCount(count)
context.portal_caches.clearAllCache()
return 'OK:%s' % count
