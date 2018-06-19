"""
================================================================================
Tear down preferences set for template test
================================================================================
"""
# parameters   (* default)
# ------------------------------------------------------------------------------

# inspired by erp5_user_tutorial_ui_test 
portal = context.getPortalObject()
zuite_preference_id = "zuite_erp5_ui_test_preference"
isTransitionPossible = portal.portal_workflow.isTransitionPossible

preference = getattr(portal.portal_preferences, zuite_preference_id, None)
if preference is None:
  preference = context.portal_preferences.newContent(
    portal_type="Preference",
    id=zuite_preference_id
  )
  if isTransitionPossible(preference, "enable"):
    preference.enable()

preference.setPreferredTextEditor("text_area")
preference.setPreferredSourceCodeEditor("text_area")
portal.portal_caches.clearAllCache()
return "Ok"
