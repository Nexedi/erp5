portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
promise_url = portal.getPromiseParameter('external_service', 'cloudooo_url')

system_preference = portal_preferences.getActiveSystemPreference()
if system_preference is None:
  system_preference = portal_preferences.newContent(
                 portal_type="System Preference", 
                 title="Created by Promise Alarms")
  system_preference.enable()

system_preference.edit(
  preferred_document_conversion_server_url=promise_url,
)
