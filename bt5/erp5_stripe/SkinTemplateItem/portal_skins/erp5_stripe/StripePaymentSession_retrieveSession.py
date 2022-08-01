import json

portal = context.getPortalObject()

response = connector.retrieveSession(session_id=context.getReference())

http_exchange = portal.system_event_module.newContent(
  portal_type="HTTP Exchange",
  title="Retrieve Session",
  follow_up_value=context,
  resource="http_exchange_resource/stripe/retrieve_session",
  response=json.dumps(response, indent=2)
)

http_exchange.confirm()
http_exchange.acknowledge()

if batch_mode:
  return http_exchange

return http_exchange.Base_redirect()
