# Proxy role auditor so new subscribers can find connector
web_service, = context.getPortalObject().portal_web_services.searchFolder(
  portal_type='Payline SOAP Connector',
  validation_state='validated',
  reference=reference,
  limit=2,
)
web_service = web_service.getObject()
assert web_service.getReference() == reference, (web_service.getPath(), reference)
return web_service
