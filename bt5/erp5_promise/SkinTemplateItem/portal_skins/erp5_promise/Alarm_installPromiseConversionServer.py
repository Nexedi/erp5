portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
promise_url = portal.getPromiseParameter('external_service', 'cloudooo_url')

domain_port = promise_url.split('//')[1].split('/')[0]
port = domain_port.split(':')[-1]
domain = domain_port[:-(len(port)+1)]

system_preference = portal_preferences.getActiveSystemPreference()
if system_preference is None:
  system_preference = portal_preferences.newContent(
                 portal_type="System Preference", 
                 title="Created by Promise Alarms")
  system_preference.enable()

system_preference.edit(
  preferred_ooodoc_server_address=domain,
  preferred_ooodoc_server_port_number=port,
)
