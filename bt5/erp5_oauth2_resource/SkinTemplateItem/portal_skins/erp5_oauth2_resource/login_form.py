# Proxy Role: Auditor to get access to the connectors
from zExceptions import BadRequest
connector_value = context.ERP5Site_getOAuth2AuthorisationClientConnectorValue(
  client_id=client_id,
)
if connector_value is None:
  if client_id:
    raise BadRequest('Invalid client_id')
  return context.skinSuper(
    'erp5_oauth2_resource',
    script.id,
  )()
return connector_value.login(
  REQUEST=REQUEST,
  RESPONSE=RESPONSE,
  came_from=came_from,
  portal_status_message=portal_status_message,
)
