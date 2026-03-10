"""
Returns the client_id of the OAuth2 Authorisation Client Connector with given id, if it is usable:
- exists
- is actually an OAuth2 Authorisation Client Connector
- is in "validated" state
- has a non-empty reference

If connector_id is None, the first usable OAuth2 Authorisation Client Connector found is used.

Can be used as a way to detect whether desired OAuth2 authentication channel is available in
custom login forms (ex: to switch to a backward-compatibility mode), or to tell a generic login
form to use a pre-selected client_id.

If chosen connector is not usable, None is returned.
"""
# Proxy Role: Auditor to get access to the connectors
if connector_id is None:
  connector_value = context.ERP5Site_getOAuth2AuthorisationClientConnectorValue(client_id=None)
else:
  try:
    connector_value = context.getPortalObject().portal_web_services[connector_id]
  except KeyError:
    connector_value = None
if (
  connector_value is not None and
  connector_value.getPortalType() == 'OAuth2 Authorisation Client Connector' and
  connector_value.getValidationState() == 'validated'
):
  return connector_value.getReference() or None
