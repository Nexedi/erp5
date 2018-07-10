"""
================================================================================
Set preference for template test to textarea
================================================================================
"""
# parameters   (* default)
# ------------------------------------------------------------------------------

# force text_area editor
context.Zuite_setPreference('')
preference = context.portal_preferences.erp5_ui_test_preference
preference.setPreferredTextEditor('text_area')
return "Editor set to Textarea."
