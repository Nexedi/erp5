# proxy role: Author and Auditor
# Proxy roles are used to create HTTP Exchange (Author) and call getPath (Auditor)
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
  store_webhook_tag = "store_webhook"
  with portal.portal_activities.defaultActivateParameterDict({"tag": store_webhook_tag}, placeless=True):
    system_event = portal.system_event_module.newContent(
      title="WebHook Response",
      portal_type="HTTP Exchange",
      response=json.dumps(data, indent=2),
      resource_value=portal.portal_categories.http_exchange_resource.stripe.webhook,
    )
    system_event.confirm()
  alarm = portal.portal_alarms.handle_confirmed_http_exchanges
  tag = "handle_confirmed_http_exchanges_webhook"
  if not portal.portal_activities.countMessage(tag=tag):
    alarm.activate(
      after_tag=store_webhook_tag,
      tag=tag
    ).activeSense()
  response.setStatus(200)
else:
  response.setStatus(400)
