"""Set subversion working copy list and enable preference.

This script is called by Products.ERP5Type.tests.runFunctionalTest to set
subversion working copy paths and conversion server address.
It's not meant to be called by zelenium tests directly.
"""

if conversion_server_url is None:
  raise TypeError("argument conversion_server_url should not be None")

pref = getattr(context.portal_preferences, "erp5_ui_test_preference", None)
if pref is None:
  pref = context.portal_preferences.newContent(id="erp5_ui_test_preference",
                                               portal_type="Preference",
                                               priority=1)

pref.setPreferredSubversionWorkingCopyList(tuple(working_copy_list.split(',')))
pref.setPreferredHtmlStyleUnsavedFormWarning(False)

if pref.getPreferenceState() == 'disabled':
  pref.enable()

pref = getattr(context.portal_preferences, "erp5_ui_test_system_preference", None)
if pref is None:
  pref = context.portal_preferences.newContent(id="erp5_ui_test_system_preference",
                                               portal_type="System Preference",
                                               priority=1)

pref.setPreferredDocumentConversionServerUrl(conversion_server_url)

if pref.getPreferenceState() == 'disabled':
  pref.enable()

return 'Set Preference Successfully.'
