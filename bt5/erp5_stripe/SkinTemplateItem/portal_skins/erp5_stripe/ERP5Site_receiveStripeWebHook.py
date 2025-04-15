# proxy role: Author to create HTTP Exchange
import json

response = container.REQUEST.RESPONSE
response.setHeader("Content-type", "application/json; charset=utf-8")

# Stripe will only POST here
if context.REQUEST["REQUEST_METHOD"] == "POST":
  portal = context.getPortalObject()
  data = json.loads(container.REQUEST.get("BODY") or "{}")
  assert data, "BODY should not be empty"
  assert "id" in data, "ID is missing"
  assert data["object"] == "event", "Unexpected object"

  system_event = portal.system_event_module.newContent(
    title="WebHook Response",
    portal_type="HTTP Exchange",
    response=json.dumps(data, indent=2),
    resource_value=portal.portal_categories.http_exchange_resource.stripe.webhook,
  )
  # Trigger the alarm before changing the event state
  # (and so, removing the access permission)
  system_event.Base_reindexAndSenseAlarm(['handle_confirmed_http_exchanges'])
  system_event.confirm()
  response.setStatus(200)
else:
  response.setStatus(400)
