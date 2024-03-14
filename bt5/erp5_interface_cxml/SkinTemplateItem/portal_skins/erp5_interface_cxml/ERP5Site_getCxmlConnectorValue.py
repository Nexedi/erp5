# Proxy Role: Auditor to get access to the connectors
for connector_value in context.portal_web_services.objectValues(portal_type='Cxml Connector'):
  if connector_value.getValidationState() == 'validated' and (
    # No network_id is provided, pick the first connector.
    network_id is None or
    # network_id provided, match it. Also matches connector in testing mode
    connector_value.getUserId().rstrip("-T") == network_id
  ):
    return connector_value
