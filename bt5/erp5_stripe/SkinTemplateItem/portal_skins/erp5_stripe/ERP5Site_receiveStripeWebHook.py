import json

response = container.REQUEST.RESPONSE
response.setHeader("Content-type", "application/json; charset=utf-8")

# Stripe will only POST here
if context.REQUEST["method"] == "POST":
  portal = context.getPortalObject()
  alarm = portal.portal_alarms.check_stripe_payment_session
  tag = "check_stripe_payment_session"
  if not portal.portal_activities.countMessage(tag=tag):
    alarm.activate(
      tag=tag
    ).activeSense()
  response.setStatus(200)
else:
  response.setStatus(400)

return json.dumps({})
