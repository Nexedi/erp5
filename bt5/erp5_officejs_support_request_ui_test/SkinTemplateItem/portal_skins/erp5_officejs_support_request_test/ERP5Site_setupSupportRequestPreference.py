portal = context.getPortalObject()
#.portal_preferences.erp5_ui_test_preference

# This should have been created during setup by Zuite_setPreference, but
# we need to support cases where developer run test in his development
# instance without the setup steps of ERP5TypeFunctionalTestCase
pref = getattr(portal.portal_preferences, "erp5_ui_test_preference", None)
if pref is None:
  pref = portal.portal_preferences.newContent(
      id="erp5_ui_test_preference",
      portal_type="Preference",
      priority=1)
if pref.getPreferenceState() == 'disabled':
  pref.enable()

# use fck editor, we test with this
pref.setPreferredTextEditor('fck_editor')

# set a preferred event resource, so that the web message we create
# gets indexed properly in stock table.
# XXX This ressource does not make much sense though, using something like
# "support request message post" would be closer to the real resource of
# these events.
preferred_event_resource = 'service_module/erp5_officejs_support_request_ui_test_service_003'
if portal.web_site_module.erp5_officejs_support_request_ui.getLayoutProperty(
    'preferred_event_resource', None) != 'preferred_event_resource':
  portal.web_site_module.erp5_officejs_support_request_ui.edit(
    preferred_event_resource=preferred_event_resource
  )

return "Done."
