error_list = []
portal = context.getPortalObject()
CLIENT_PORTAL_TYPE = 'OAuth2 Authorisation Client Connector'
CONNECTOR_PORTAL_TYPE_SET = (
  CLIENT_PORTAL_TYPE,
  'OAuth2 Authorisation Server Connector',
)
if CLIENT_PORTAL_TYPE in portal.portal_types:
  # erp5_oauth2_resource (or whatever welse could contain the OAuth2 client-side)
  # is installed along with us (the server half), assume admin intends for local
  # authentication to be handled by OAuth2 (they may invalidate the connectors
  # created here if this is not their intention).
  # Also, register authorisation extractor, as required by .
  if not portal.isAuthorisationExtractorEnabled():
    error_list.append('ERP5Site authorisation extractor is not registered')
    if fixit:
      portal.enableAuthorisationExtractor()
  portal_web_services = portal.portal_web_services
  for connector_value in portal_web_services.objectValues():
    if connector_value.getPortalType() in CONNECTOR_PORTAL_TYPE_SET:
      # Some connector already exists (do not care about their state,
      # admin may have decided to invalidate them), nothing to do.
      break
  else:
    error_list.append('Local OAuth2 authentication is missing')
    if fixit:
      server_connector_value = portal_web_services.newContent(
        portal_type='OAuth2 Authorisation Server Connector',
      )
      server_connector_value.validate()
      client_declaration_value = server_connector_value.newContent(
        portal_type='OAuth2 Client',
        title='Local authentication',
        local=True,
      )
      portal_web_services.newContent(
        portal_type='OAuth2 Authorisation Client Connector',
        title='Local authentication',
        reference=client_declaration_value.getId(),
        authorisation_server_url=server_connector_value.getId(),
      ).validate()
      client_declaration_value.validate()
return error_list
