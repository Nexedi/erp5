# proxy role: Author and Auditor
# Proxy roles are used to create HTTP Exchange (Author) and call getPath (Auditor)
import json

response = container.REQUEST.RESPONSE
response.setHeader("Content-type", "application/json; charset=utf-8")

# Stripe will only POST here
if context.REQUEST["method"] == "POST":
  portal = context.getPortalObject()
  data = json.loads(container.REQUEST.get("BODY") or "{}")
  assert data, "BODY should not be empty"
  assert "id" in data, "ID is missing"
  assert data["object"] == "event", "Unexpected object"
  system_event = portal.system_event_module.newContent(
    title="WebHook Response",
    portal_type="HTTP Exchange",
    response=json.dumps(data, indent=2),
    resource="http_exchange_resource/stripe/webhook",
  )
  system_event.confirm()
  
  portal = context.getPortalObject()
  alarm = portal.portal_alarms.handle_confirmed_http_exchanges
  tag = "handle_confirmed_http_exchanges_webhook"
  if not portal.portal_activities.countMessage(tag=tag):
    alarm.activate(
      after_path_and_method_id=(
        (system_event.getPath(),),
        ("immediateReindexObject",)
      ),
      tag=tag
    ).activeSense()
  response.setStatus(200)
else:
  response.setStatus(400)
