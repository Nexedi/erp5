"""Set subversion working copy list and enable preference.

This script is called by Products.ERP5Type.tests.runFunctionalTest to set
subversion working copy paths and conversion server address.
It's not meant to be called by zelenium tests directly.
"""
context.Zuite_setPreference('')
pref = context.portal_preferences.erp5_ui_test_preference

# pref.setPreferredTextEditor('fck_editor')

return 'Set Bank Reconciliation Preference Successfully.'
