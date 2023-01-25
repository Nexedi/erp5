# Proxy Role: Auditor to get access to the connectors
connector_value_list = [
  x
  for x in context.portal_web_services.objectValues(portal_type='OAuth2 Authorisation Client Connector')
  if x.getValidationState() == 'validated'
]
if client_id is None:
  # Caller did not express a preference...
  # - if any connector is marked as usable by default, only keep connectors which have such mark.
  connector_value_list = [
    x
    for x in connector_value_list
    if x.isUsableAsDefault()
  ] or connector_value_list
  # - prefer local authentication if available.
  connector_value_list.sort(key=lambda x: x.isAuthorisationServerRemote())
for connector_value in connector_value_list:
  if (
    # No client_id is provided, pick the first connector.
    client_id is None or
    # client_id provided, match it.
    connector_value.getReference() == client_id
  ):
    return connector_value
